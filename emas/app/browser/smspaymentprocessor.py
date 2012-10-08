from five import grok

from AccessControl import Unauthorized 

from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager

from emas.theme.interfaces import IEmasSettings


class SMSPaymentApproved(grok.View):
    """ Reverse tunnel from siyavula:
        ssh -nNT -R 9999:localhost:8080 siyavula
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    
    def update(self):
        self.validated = self.validateSender(self.context, self.request)
        self.order = self.getOrder(self.context, self.request)

    def render(self):
        import pdb;pdb.set_trace()
        if self.validated:
            # do the transition
            self.transitionToPaid(self.context, self.request, self.order)

            # send notification
            
            return
        else:
            raise Unauthorized()
    
    def getOrder(self, context, request):
        import pdb;pdb.set_trace()
        verification_code = request.get('verification_code')
        if not verification_code:
            return None

        member = context.restrictedTraverse('@@plone_portal_state').member()
        pc = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type':       'emas.app.order',
                 'verification_code': verification_code,
                 'memberid':          member.getId()}
        brains = pc(query)
        if not brains or len(brains) < 1:
            return None
        
        return brains[0].getObject()

    def validateSender(self, context, request):
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)
        password = request.get('password')
        return password == self.settings.bulksms_password

    def transitionToPaid(self, context, request, order):
        pms = getToolByName(context, 'portal_membership')
        member = pms.getMemberById(order.userid)
        newSecurityManager(request, member)
        wf = getToolByName(context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', order)
        if status['review_state'] != 'paid':
            wf.doActionFor(order, 'pay')
            order.reindexObject()

    def setNotification(self, request, context):
        return
