from five import grok
from Acquisition import aq_inner

from plone.registry.interfaces import IRegistry

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from zope.interface import Interface
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName

from emas.theme.interfaces import IEmasSettings


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
        status = wf.getStatusOf('order_workflow', self.order)
        if status['review_state'] != 'paid':
            pps = self.context.restrictedTraverse('@@plone_portal_state')
            portal = pps.portal()

            settings = queryUtility(IRegistry).forInterface(IEmasSettings)
            userid = settings.vcs_user_id
            user = portal.acl_users.getUserById(userid)

            old_security_manager = getSecurityManager()
            newSecurityManager(self.request, user)

            try:
                wf.doActionFor(self.order, 'pay')
                self.order.reindexObject()
            finally:
                # restore the original Security Managemer
                setSecurityManager(old_security_manager)

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

        wf = getToolByName(self.context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', self.order)
        if status['review_state'] != 'paid':
            wf.doActionFor(self.order, 'pay')
            self.order.reindexObject()
       

    def render(self):
        return ''
