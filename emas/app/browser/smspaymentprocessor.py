import urllib
from five import grok
from logging import getLogger
from AccessControl import Unauthorized 

from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager

from emas.theme.interfaces import IEmasSettings

LOGGER = getLogger('emas.app:smspaymentprocessor')

class SMSPaymentApproved(grok.View):
    """ Reverse tunnel from siyavula:
        ssh -nNT -R 9999:localhost:8080 siyavula
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    
    def update(self):
        self.order = self.getOrder(self.context, self.request)

        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)
        self.validated = self.validateSender(self.request, self.settings)

        if self.order and self.validated:
            # do the transition
            self.transitionToPaid(self.context, self.request, self.order)

            # send notification
            self.sendNotification(self.request,
                                  self.context,
                                  self.order,
                                  self.settings)

    def render(self):
        if self.order:
            if self.validated:
                return 'Order %s is now paid.' % self.order.getId()
            else:
                raise Unauthorized()
        else:
            return self.request.response.notFoundError('Order')
    
    def getOrder(self, context, request):
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
            LOGGER.info(
                'Could not find order with verification code:'
                '%s' % verification_code)
            return None
        
        return brains[0].getObject()

    def validateSender(self, request, settings):
        password = request.get('password')
        return password == settings.bulksms_receive_password

    def transitionToPaid(self, context, request, order):
        pms = getToolByName(context, 'portal_membership')
        member = pms.getMemberById(order.userid)
        newSecurityManager(request, member)
        wf = getToolByName(context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', order)
        if status['review_state'] != 'paid':
            wf.doActionFor(order, 'pay')
            order.reindexObject()

    def sendNotification(self, request, context, order, settings):
        msisdn = self.request.get('sender', '')
        if not msisdn:
            LOGGER.warn('No recipient msisdn specified')
            return

        username = settings.bulksms_send_username
        password = settings.bulksms_send_password
        url = settings.bulksms_send_url
        message = 'Payment received for order:%s.' % self.order.getId()
        params = urllib.urlencode({'username' : username,
                                   'password' : password,
                                   'message'  : message,
                                   'msisdn'   : msisdn})

        f = urllib.urlopen(url, params)
        s = f.read()
        f.close()

        result = s.split('|')
        statusCode = result[0]
        statusString = result[1]
        if statusCode != '0':
                message = "Error: " + statusCode + ": " + statusString
                raise Unauthorized(message)
        else:
                LOGGER.info('Message sent: batch ID %s' % result[2])
