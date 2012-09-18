from email.Utils import formataddr

from five import grok
from Acquisition import aq_inner
from zope.component import queryUtility
from zope.interface import Interface
from z3c.relationfield.relation import create_relation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings

SERVICE_SELECTION      = 'service_selection'
SELECTION_CONFIRMATION = 'selection_confirmation'

grok.templatedir('templates')

class Purchase(grok.View):
    """
        A 2 stage form that captures the services and products a user wants
        to buy.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('purchase')

    ordertemplate = ViewPageTemplateFile('templates/ordermailtemplate.pt')
    ordernotification = ViewPageTemplateFile('templates/ordernotification.pt')
    
    def update(self):
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)
        self.mode = SERVICE_SELECTION
        self.selected_services = []

        if self.request.get('purchase.form.submitted'):
            order_items = self.request.form.get('order')
            if order_items is None or len(order_items) < 1:
                # no items selected, show the selection UI
                self.mode = SERVICE_SELECTION
           
            # set local variables for use in the template
            self.mode = SELECTION_CONFIRMATION
            self.selected_services = order_items
            
        elif self.request.get('purchase.confirmed'):
            # create member service objects
            portal_state = self.context.restrictedTraverse(
                '@@plone_portal_state'
            )
            portal = portal_state.portal()
            member = portal_state.member()
            memberid = member.getId()
            member_orders = portal['orders']
            products_and_services = portal['products_and_services']
        
            order_items = self.request.form.get('order')
            if order_items is None or len(order_items) < 1:
                # no items selected, show the selection UI
                self.mode = SERVICE_SELECTION
            
            ordernumber = self.settings.order_sequence_number + 1
            self.settings.order_sequence_number = ordernumber
            self.ordernumber = '%04d' % ordernumber
            member_orders.invokeFactory(
                type_name='emas.app.order',
                id=self.ordernumber,
                title=self.ordernumber,
                userid=memberid
            )
            self.order = member_orders._getOb(self.ordernumber)

            for sid, quantity in order_items.items():
                service = products_and_services[sid]
                relation = create_relation(service.getPhysicalPath())
                item_id = self.order.generateUniqueId(type_name='orderitem')
                self.order.invokeFactory(
                    type_name='emas.app.orderitem',
                    id=item_id,
                    title=item_id,
                    related_item=relation,
                    quantity=quantity,
                )
            
            self.request.response.redirect(
                '@@paymentdetails/?orderid=%s' %self.order.getId())
    
    def products_and_services(self):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        products_and_services = pps.portal()._getOb('products_and_services')
        return products_and_services.getFolderContents(full_objects=True)

