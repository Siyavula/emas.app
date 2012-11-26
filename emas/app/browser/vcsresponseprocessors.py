import logging

from five import grok
from Acquisition import aq_inner

from plone.registry.interfaces import IRegistry

from zope.interface import Interface
from zope.component import queryUtility
from AccessControl.SecurityManagement import newSecurityManager

from Products.CMFCore.utils import getToolByName

from emas.app.browser.utils import get_display_items_from_order
from emas.app.browser.utils import member_services
from emas.app.browser.utils import practice_service_uuids
from emas.app.browser.utils import service_url as get_service_url

LOGGER = logging.getLogger(__name__)

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
        LOGGER.info(self.request)
        self.pps = self.context.restrictedTraverse('@@plone_portal_state')
        pms = getToolByName(self.context, 'portal_membership')

        oid = self.request.get('p2')
        self.order = getOrder(self.context, self.request)

        member = pms.getMemberById(self.order.userid)
        newSecurityManager(self.request, member)
        wf = getToolByName(self.context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', self.order)
        if status['review_state'] != 'paid':
            wf.doActionFor(self.order, 'pay')
            self.order.reindexObject()

        # we put 'm_1', the absolute_url of the context, in as parameter to the
        # initial VCS call.  If it is returned we want to show the approved page
        # in that context rather than the current context, which could be the
        # root of the plone site.
        original_url = self.request.get('m_1', None)
        if original_url is not None and len(original_url) > 0:
            # add p2 as url parameter since we are redirecting back to
            # the same view and need to look up the order again
            url = original_url + '/@@paymentapproved?p2=%s' % oid
            self.request.response.redirect(url)
    
    def memberservices(self):
        return get_display_items_from_order(self.order)
    
    def service_url(self, service):
        return get_service_url(service)


class PaymentDeclined(grok.View):
    """
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    
    def update(self):
        original_url = self.request.get('m_1', None)
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

        wf = getToolByName(self.context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', self.order)
        if status['review_state'] != 'paid':
            wf.doActionFor(self.order, 'pay')
            self.order.reindexObject()
       

    def render(self):
        return ''
