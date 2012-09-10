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

class Confirm(grok.View):
    """ Conform an order.
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

            for sid, quantity in self.selected_services.items():
                service = self.products_and_services[sid]
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
                selected_items[sid] = quantity

        return selected_items

    def ordersubmitted(self):
        return self.request.has_key('order.form.submitted')
