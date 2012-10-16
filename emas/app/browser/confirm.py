import hashlib
from itertools import chain
from email.Utils import formataddr

from five import grok
from Acquisition import aq_inner
from zope.component import queryUtility
from zope.interface import Interface
from z3c.relationfield.relation import create_relation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.utils import createContentInContainer

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings
from emas.app.browser.utils import annotate
from emas.app.order import CREDITCARD, SMS, EFT

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

        self.display_items = self._display_items()
        # get the discount sorted out
        self.discount_items = self._discount_items(self.display_items)
        self.selected_items = dict(
            chain(self.display_items.items(), self.discount_items.items())
        )

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
            self.order.phone= self.request.get('phone', '')
            self.order.shipping_address = self.request.get('shipping_address', '')
            self.order.payment_method = self.prod_payment()

            for service, quantity in self.selected_items.items():
                item_id = 'orderitem.%s' %service.getId()
                relation = create_relation(service.getPhysicalPath())
                props = {'id'           :item_id,
                         'title'        :service.Title(),
                         'related_item' :relation,
                         'quantity'     :quantity}
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
        elif order.payment_method == SMS:
            self.prepSMSPayment(order, request)

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
        # generate payment verification code
        m = hashlib.md5()
        m.update(
            self.memberid + 
            self.order.getId() + 
            self.settings.bulksms_send_password)
        verification_code = m.hexdigest()[:6]
        order.verification_code = verification_code
        order.reindexObject(idxs=['verification_code'])

    def _display_items(self):
        """ TODO: move to utils.display_items ASAP
        """
        display_items = {}
        # the submitted form data looks like this:
        #{'order.form.submitted': 'true',
        #'prod_practice_book': 'Practice,Textbook',
        #'practice_subjects': 'Maths,Science',
        #'submit': '1',
        #'practice_grade': 'Grade 10'}
        self.grade = self.request.form.get('grade', '')
        self.prod_practice_book = self.request.form.get('prod_practice_book', '')
        self.subjects = self.request.form.get('subjects', '')
        for subject in self.subjects.split(','):
            for item in self.prod_practice_book.split(','):
                # e.g. subject-grade-[practice | questions | textbook]
                sid = '%s-%s-%s' %(subject, self.grade, item)
                sid = sid.replace(' ', '-').lower()
                quantity = display_items.get(sid, 0) +1
                service = self.products_and_services._getOb(sid)
                display_items[service] = quantity
                
        return display_items

    def _discount_items(self, selected_items): 
        discount_items = {}
        deals = {'maths-grade10-discount'   :['maths-grade10-practice',
                                              'maths-grade10-textbook'],
                 'science-grade10-discount' :['science-grade10-practice',
                                              'science-grade10-textbook'],
                 'maths-grade11-discount'   :['maths-grade11-practice',
                                              'maths-grade11-textbook'],
                 'science-grade11-discount' :['science-grade11-practice',
                                              'science-grade11-textbook'],
                 'maths-grade12-discount'   :['maths-grade12-practice',
                                              'maths-grade12-textbook'],
                 'science-grade12-discount' :['science-grade12-practice',
                                              'science-grade12-textbook'], }
        
        selected_items = set(selected_items.keys())
        for discount_id, items in deals.items():
            deal_items = \
                set([self.products_and_services._getOb(item) for item in items])

            common_items = selected_items.intersection(deal_items)
            if len(common_items) == len(deal_items):
                discount_service = self.products_and_services._getOb(discount_id)
                quantity = discount_items.get(discount_service.getId(), 0) +1
                discount_items[discount_service] = quantity

        return discount_items

    def ordersubmitted(self):
        return self.request.has_key('order.form.submitted')

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

        subject = 'Order from %s Website' % state.navigation_root_title()

        fullname=member.getProperty('fullname')
        sitename=state.navigation_root_title()
        items = order.order_items()
        totalcost=order.total()
        username=member.getId()
        email=self.settings.order_email_address
        phone=self.settings.order_phone_number

        # Generate message and attach to mail message
        message = self.ordertemplate(
            fullname=fullname,
            sitename=sitename,
            orderitems=self.display_items.keys(),
            totalcost=totalcost,
            username=username,
            ordernumber=self.ordernumber,
            email=email,
            phone=phone,
            payment=self.prod_payment(),
        )

        portal.MailHost.send(message, send_to_address, send_from_address,
                             subject, charset=encoding)

        subject = 'New Order placed on %s Website' % \
            state.navigation_root_title()

        # Generate order notification
        message = self.ordernotification(
            fullname=fullname,
            sitename=sitename,
            orderitems=self.display_items.keys(),
            totalcost=totalcost,
            orderurl=order.absolute_url(),
            username=username,
            ordernumber=self.ordernumber,
            email=email,
            phone=phone,
            payment=self.prod_payment(),
        )

        # Siyavula's copy
        portal.MailHost.send(message, send_from_address, send_from_address,
                             subject, charset=encoding)
