from five import grok
from Acquisition import aq_inner

from zope.interface import Interface


grok.templatedir('templates')


def getOrder(context, request):
    # the original transaction id will be returned as 'p2'
    oid = request['p2']

    pps = context.restrictedTraverse('@@plone_portal_state')
    portal = pps.portal()
    orders = portal._getOb('orders')
    return orders._getOb(oid)


class PaymentApproved(grok.View):
    """
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    
    def update(self):
        self.order = getOrder(self.context, self.request)

        wf = getToolByName(self.context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', item)
        if status['review_state'] != 'paid':
            wf.doActionFor(order, 'pay')
            order.reindexObject()
       
        # we put 'm1', the absolute_url of the context, in as a parameter to the
        # initial VCS call.  If it is returned we want to show the approved page
        # in that context rather than the current context, which could be the
        # root of the plone site.
        original_url = self.request.get('m1', None)
        if original_url is not None and len(original_url) > 0:
            url = original_url + '/@@paymentapproved'
            self.request.response.redirect(url)
    

class PaymentDeclined(grok.View):
    """
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    
    def update(self):
        original_url = self.request.get('m1', None)
        if original_url is not None and len(original_url) > 0:
            url = original_url + '/@@paymentdeclined'
            self.request.response.redirect(url)


class Callback(grok.View):
    """
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    
    def update(self):
        self.order = getOrder(self.context, self.request)

    def render(self):
        return ''
