from five import grok
from Acquisition import aq_inner

from plone.registry.interfaces import IRegistry

from zope.interface import Interface
from zope.component import queryUtility
from AccessControl.SecurityManagement import newSecurityManager

from Products.CMFCore.utils import getToolByName

from emas.theme.interfaces import IEmasSettings

from emas.app.browser.utils import practice_service_uuids, member_services

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
        self.pps = self.context.restrictedTraverse('@@plone_portal_state')
        pms = getToolByName(self.context, 'portal_membership')
        # on the first pass after VCS the request will have a 'p2' var
        # then we do the rest. Otherwise, just render the template.
        if self.request.has_key('p2'):
            self.order = getOrder(self.context, self.request)
            member = pms.getMemberById(self.order.userid)
            newSecurityManager(self.request, member)
            wf = getToolByName(self.context, 'portal_workflow')
            status = wf.getStatusOf('order_workflow', self.order)
            if status['review_state'] != 'paid':
                wf.doActionFor(self.order, 'pay', request=self.request)
                self.order.reindexObject()

        # we put 'm_1', the absolute_url of the context, in as parameter to the
        # initial VCS call.  If it is returned we want to show the approved page
        # in that context rather than the current context, which could be the
        # root of the plone site.
        original_url = self.request.get('m_1', None)
        if original_url is not None and len(original_url) > 0:
            url = original_url + '/@@paymentapproved'
            self.request.response.redirect(url)
    
    def memberservices(self):
        uids = practice_service_uuids(self.context)
        memberservices = member_services(self.context, uids)
        return memberservices
    
    def service_url(self, service):
        portal_url = self.pps.portal().absolute_url()
        grade = service.related_service.to_object.grade
        return '%s/@@practice/%s' %(portal_url, grade)


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
