import hashlib
from email.Utils import formataddr

from five import grok
from Acquisition import aq_inner
from zope.component import queryUtility
from zope.interface import Interface
from z3c.relationfield.relation import create_relation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings

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
        self.member_orders = self.portal['orders']
        self.products_and_services = self.portal['products_and_services']

        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)

        self.selected_services = self.selected_services()
        self.ordernumber = ''

        if self.ordersubmitted():
            # create member service objects
            tmpnumber = self.settings.order_sequence_number + 1
            self.settings.order_sequence_number = tmpnumber
            self.ordernumber = '%04d' % tmpnumber
            self.member_orders.invokeFactory(
                type_name='emas.app.order',
                id=self.ordernumber,
                title=self.ordernumber,
                userid=self.memberid
            )
            self.order = self.member_orders._getOb(self.ordernumber)

            # set the shipping address if we have one
            self.order.fullname = self.request.get('fullname', '')
            self.order.phone= self.request.get('phone', '')
            self.order.shipping_address = self.request.get('shipping_address', '')

            for service, quantity in self.selected_services.items():
                relation = create_relation(service.getPhysicalPath())
                item_id = self.order.generateUniqueId(type_name='orderitem')
                self.order.invokeFactory(
                    type_name='emas.app.orderitem',
                    id=item_id,
                    title=item_id,
                    related_item=relation,
                    quantity=quantity,
                )
            self.totalcost = self.order.total()

            self.prepVCS()

    def prepVCS(self):
        # when debugging you can use this action to return to the approved
        # page immediately.
        # self.action = '%s/@@paymentapproved' %self.context.absolute_url()

        # becomes the action to which the page is posted.
        self.action = self.settings.vcs_url

        # terminal id; becomes p1 in the template
        self.vcs_terminal_id = self.settings.vcs_terminal_id

        # no orderid, no processing possible. So we raise an error.
        # becomes p2 in the template
        self.tid = self.order.getId() 
        if self.tid == None or len(self.tid) < 1:
            raise AttributeError('No orderid supplied')

        # becomes p3 in the template
        self.description = 'Siyavula EMAS %s' %self.order.Title()
        
        # becomes p4 in the template
        self.cost = self.order.total()
        self.quantity = 1

        # the return url passed as m_1 in the template
        self.returnurl = self.context.absolute_url()

        self.md5key = self.settings.vcs_md5_key

        self.md5hash = vcs_hash(self.vcs_terminal_id + self.tid + 
                                self.description + str(self.cost) +
                                self.returnurl + self.md5key)

    def selected_services(self):
        selected_items = {}
        # the submitted form data looks like this:
        #{'order.form.submitted': 'true',
        #'prod_practice_book': 'Practice,Textbook',
        #'practice_subjects': 'Maths,Science',
        #'submit': '1',
        #'practice_grade': 'Grade 10'}
        grade = self.request.form['grade']
        selected = self.request.form['prod_practice_book'].split(',')
        subjects = self.request.form['subjects'].split(',')
        # subject + grade + practice | questions | textbook
        for subject in subjects:
            for item in selected:
                sid = '%s-%s-%s' %(subject, grade, item)
                sid = sid.replace(' ', '-').lower()
                quantity = selected_items.get(sid, 0) +1
                service = self.products_and_services._getOb(sid)
                selected_items[service] = quantity

        return selected_items

    def ordersubmitted(self):
        return self.request.has_key('order.form.submitted')

    def creditcard_selected(self):
        payment = self.request.get('prod_payment', '')
        return payment == 'creditcard' and 'checked' or ''

    def eft_selected(self):
        payment = self.request.get('prod_payment', '')
        return payment == 'eft' and 'checked' or ''
