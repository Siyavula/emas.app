import random
import hashlib
import logging
from itertools import chain
from email.Utils import formataddr

from five import grok
from Acquisition import aq_inner
from zope.component import queryUtility
from zope.interface import Interface
from z3c.relationfield.relation import create_relation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.utils import createContentInContainer

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

# Yuck, app should ideally not depend on theme
from emas.theme.interfaces import IEmasSettings
from emas.app.order import CREDITCARD, SMS, EFT
from emas.app.service import IService
from emas.app.browser.utils import (
    annotate,
    get_paid_orders_for_member,
    generate_verification_code
    )

LOGGER = logging.getLogger(__name__)

grok.templatedir('templates')

def vcs_hash(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


class Confirm(grok.View):
    """ Confirm an order.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    ordertemplate = ViewPageTemplateFile('templates/ordermailtemplate.pt')
    ordernotification = ViewPageTemplateFile('templates/ordernotification.pt')
    
    retries = 1000
    lower = 9999
    upper = 100000

    def update(self):
        self.portal_state = self.context.restrictedTraverse(
            '@@plone_portal_state'
        )
        self.portal = self.portal_state.portal()
        self.member = self.portal_state.member()
        self.memberid = self.member.getId()
        self.orders = self.portal['orders']
        self.products_and_services = self.portal['products_and_services']

        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)

        self.subjects = self.request.get('subjects')
        self.service_ordered = self._service_ordered()

        self.ordernumber = ordernumber = self.request.get('ordernumber', '')

        if self.ordersubmitted():

            if self.request.has_key('confirm_back_button'):
                return self.context.restrictedTraverse('@@order')

            if ordernumber:
                self.order = self.orders._getOb(self.ordernumber)
                self.order.manage_delObjects(self.order.objectIds()) 
            else:
                tmpnumber = self.settings.order_sequence_number + 1
                self.settings.order_sequence_number = tmpnumber
                self.ordernumber = '%04d' % tmpnumber
                props = {'id'     :self.ordernumber,
                         'title'  :self.ordernumber,
                         'userid' :self.memberid}
                createContentInContainer(
                    self.orders,
                    'emas.app.order',
                    False,
                    **props
                )
                self.order = self.orders._getOb(self.ordernumber)

            self.order.fullname = self.request.get('fullname', '')
            self.order.phone = self.request.get('phone', '')
            self.order.shipping_address = self.request.get('shipping_address', '')
            self.order.payment_method = self.prod_payment()

            ordered_service_ids = []

            # mobile order
            if self.request.get('service') == 'monthly-practice':
                sid = '%s-grade12-monthly-practice' % self.subjects.lower()
                ordered_service_ids.append(sid)

            # web order
            else:
                maths_service_ids = [
                    'maths-grade12-practice',
                ]
                science_service_ids = [
                    'science-grade12-practice',
                ]
                if self.subjects in ('Maths', 'Maths,Science'):
                    ordered_service_ids.extend(maths_service_ids)
                if self.subjects in ('Science', 'Maths,Science'):
                    ordered_service_ids.extend(science_service_ids)
                # add discount if both subjects were ordered
                if self.subjects == 'Maths,Science':
                    ordered_service_ids.append('maths-and-science-discount')

            for sid in ordered_service_ids:
                service = self.products_and_services[sid]
                item_id = 'orderitem.%s' %service.getId()
                relation = create_relation(service.getPhysicalPath())
                quantity = 1
                props = {'id': item_id,
                         'title': service.Title(),
                         'related_item': relation,
                         'quantity': quantity}
                createContentInContainer(
                    self.order,
                    'emas.app.orderitem',
                    False,
                    **props
                )

            self.totalcost = "R %.2f" % self.order.total()
            
            # Now we do the payment bit. Since it can be one of several ways we
            # wrap the lot in a seperate method.
            self.prepPaymentDetails(self.order, self.request)

            # We can only send an invoice if we have somewhere to send it to.
            if self.member.getProperty('email'):
                self.send_invoice(self.order)

    def prepPaymentDetails(self, order, request):
        """ TODO:
            Discuss adding payment processors as utilities.
            Mark them with interface IPaymentProcessor.
            Mark them with specific payment type interfaces too, eg.
            - IVCSPaymentProcessor, ISMSPaymentProcessor, IEFTPaymentProcessor.
            Lookup the correct utility, based on the selected payment method.
            Tell it do to the transaction.
        """
        if order.payment_method == CREDITCARD:
            self.prepVCSPayment(order, request)
            # write all the details to the log for debugging, etc.
            self.logVCSDetails()
        elif order.payment_method == SMS:
            self.prepSMSPayment(order, request)
            # write all the details to the log for debugging, etc.
            self.logSMSDetails()

    def warnings(self):
        """ Find all the current member's active memberservices.
            Use that to compute the related services.
            Compare that to the current order's services.
            If there are matches, return a list of those that match.

            We do this in order to warn the user that he might be ordering and
            paying for a service or product again.
        """
        ordered_services = []
        ordered_products = []
        for oi in self.order.order_items():
            r_item = oi.related_item.to_object
            if IService.providedBy(r_item):
                ordered_services.append(r_item)
            else:
                ordered_products.append(r_item)
        ordered_services = set(ordered_services)
        ordered_products = set(ordered_products)
            
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        memberid = pps.member().getId()
        orders = get_paid_orders_for_member(self.context, memberid)
        paid_products = []
        paid_services = []
        for order in orders:
            for item in order.order_items():
                r_item = item.related_item.to_object
                if r_item is None:
                    continue
                if 'discount' in r_item.title.lower():
                    continue

                if IService.providedBy(r_item):
                    paid_services.append(r_item)
                else:
                    paid_products.append(r_item)

        paid_services = set(paid_services)
        paid_products = set(paid_products)
        
        matching_products = paid_products.intersection(ordered_products)
        matching_services = paid_services.intersection(ordered_services)
        return matching_products.union(matching_services)

    def prepVCSPayment(self, order, request):
        # when debugging you can use this action to return to the approved
        # page immediately.
        # self.action = '%s/@@paymentapproved' %self.context.absolute_url()

        # becomes the action to which the page is posted.
        self.action = self.settings.vcs_url

        # terminal id; becomes p1 in the template
        self.vcs_terminal_id = self.settings.vcs_terminal_id

        # no orderid, no processing possible. So we raise an error.
        # becomes p2 in the template
        self.tid = order.getId() 
        if self.tid == None or len(self.tid) < 1:
            raise AttributeError('No orderid supplied')

        # becomes p3 in the template
        self.description = 'Siyavula EMAS %s' % order.Title()
        
        # becomes p4 in the template
        self.cost = order.total()
        self.quantity = 1

        # the return url passed as m_1 in the template
        self.returnurl = self.context.absolute_url()

        self.md5key = self.settings.vcs_md5_key

        self.md5hash = vcs_hash(self.vcs_terminal_id + self.tid + 
                                self.description + str(self.cost) +
                                self.returnurl + self.md5key)

        annotate(order, 'vcs_hash', self.md5hash)

    def prepSMSPayment(self, order, request):
        # used in template as the action to which the form is submitted.
        self.action = '.'

        # generate payment verification code
        verification_code = generate_verification_code(order)
        order.verification_code = verification_code
        order.reindexObject(idxs=['verification_code'])

    def logVCSDetails(self):
        details = {'OrderNumber': self.ordernumber,
                   'Action': self.action,
                   'CreditCardSelected': self.creditcard_selected(),
                   'orderid': self.order.getId(),
                   'p1': self.vcs_terminal_id,
                   'p2': self.tid,
                   'p3': self.description,
                   'p4': self.cost,
                   'm_1': self.returnurl,
                   'hash': self.md5hash,
                   'prod_payment': self.creditcard_selected(),
                  }
        LOGGER.info(details)

    def logSMSDetails(self):
        details = {'OrderNumber': self.ordernumber,
                   'Action': self.action,
                   'prod_payment': 'SMS',
                   'verification_code': self.order.verification_code
                  }
        LOGGER.info(details)

    def _service_ordered(self):
        if self.request.get('service') == 'monthly-practice':
            substr = "1 month subscription to %s"
            return substr % self.subjects
        else:
            if self.subjects in ('Maths'):
                return "1 year subscription to Maths"
            if self.subjects in ('Science'):
                return "1 year subscription to Science"
            elif self.subjects == 'Maths,Science':
                return "1 year subscription to Maths and Science"

    def ordersubmitted(self):
        return (self.request.has_key('order.form.submitted') or
                self.request.has_key('mobileorder.form.submitted'))

    def prod_payment(self):
        return self.request.get('prod_payment', '')

    def creditcard_selected(self):
        payment = self.request.get('prod_payment', '')
        return payment == CREDITCARD and 'checked' or ''

    def eft_selected(self):
        payment = self.request.get('prod_payment', '')
        return payment == EFT and 'checked' or ''

    def sms_selected(self):
        payment = self.request.get('prod_payment', '')
        return payment == SMS and 'checked' or ''

    def premium_number(self):
        return self.settings.bulksms_premium_number 

    def verification_code(self):
        return self.order.verification_code

    def fullname(self):
        return self.request.get('fullname', '')

    def phone(self):
        return self.request.get('phone', '')

    def shipping_address(self):
        return self.request.get('shipping_address', '')

    def email_send_count(self):
        return self.request.get('email_send_count', 0) +1
    
    def send_invoice(self, order): 
        """ Send Invoice to recipients
        """
        state = self.context.restrictedTraverse('@@plone_portal_state')
        portal = state.portal()
        member = state.member()
        host = portal.MailHost
        encoding = portal.getProperty('email_charset')

        send_from_address = formataddr(
            ( 'Siyavula Education', self.settings.order_email_address )
        )
        
        send_to_address = formataddr((member.getProperty('fullname'),
                                      member.getProperty('email')))

        subject = 'Your order for maths and science practice'

        fullname=member.getProperty('fullname')
        sitename=state.navigation_root_title()
        items = order.order_items()
        totalcost=order.total()
        username=member.getId()
        email=self.settings.order_email_address
        phone=self.settings.order_phone_number
        site_url = state.portal_url()

        # Generate message and attach to mail message
        message = self.ordertemplate(
            fullname=fullname,
            sitename=sitename,
            service_ordered=self.service_ordered,
            totalcost=totalcost,
            username=username,
            ordernumber=self.ordernumber,
            email=email,
            phone=phone,
            payment=self.prod_payment(),
            verification_code=self.verification_code,
            premium_number=self.premium_number(),
            site_url=site_url,
        )

        portal.MailHost.send(message, send_to_address, send_from_address,
                             subject, charset=encoding)

        subject = 'New Order placed on %s' % site_url

        # Generate order notification
        message = self.ordernotification(
            fullname=fullname,
            sitename=sitename,
            service_ordered=self.service_ordered,
            totalcost=totalcost,
            orderurl=order.absolute_url(),
            username=username,
            ordernumber=self.ordernumber,
            email=email,
            phone=phone,
            payment=self.prod_payment(),
            site_url=site_url,
        )

        # Siyavula's copy
        portal.MailHost.send(message, send_from_address, send_from_address,
                             subject, charset=encoding)
