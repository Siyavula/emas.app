from five import grok
from Acquisition import aq_inner

from zope.interface import Interface
from z3c.relationfield.relation import create_relation


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

    
    def update(self):
        # set local variables for use in the template
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
            portal_state = self.context.restrictedTraverse('@@plone_portal_state')
            portal = portal_state.portal()
            member = portal_state.member()
            memberid = member.getId()
            member_orders = portal['orders']
            products_and_services = portal['products_and_services']
        
            order_items = self.request.form.get('order')
            if order_items is None or len(order_items) < 1:
                # no items selected, show the selection UI
                self.mode = SERVICE_SELECTION

            order_id = member_orders.generateUniqueId(type_name='order')
            member_orders.invokeFactory(
                type_name='emas.app.order',
                id=order_id,
                title=order_id,
                userid=memberid
            )
            order = member_orders._getOb(order_id)

            for sid, quantity in order_items.items():
                service = products_and_services[sid]
                relation = create_relation(service.getPhysicalPath())
                item_id = order.generateUniqueId(type_name='orderitem')
                order.invokeFactory(
                    type_name='emas.app.orderitem',
                    id=item_id,
                    title=item_id,
                    related_item=relation,
                    quantity=quantity,
                )

            self.request.response.redirect(self.context.absolute_url())
