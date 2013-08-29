import urllib
from five import grok
from logging import getLogger
from AccessControl import Unauthorized 

from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from emas.theme.interfaces import IEmasSettings

LOGGER = getLogger('emas.app:smspaymentprocessor')

ADMIN_USER_ID = 'admin'

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
        self.logRequest(self.request)
        self.validated = self.validateSender(self.request, self.settings)

        if self.order and self.validated:
            # do the transition
            self.transitionToPaid(self.context, self.request, self.order)
            LOGGER.info('Order:%s transitioned to paid' % self.order.getId())

            # send notification
            self.sendNotification(self.request,
                                  self.context,
                                  self.order,
                                  self.settings)
            LOGGER.info('Notification sent')
        else:
            LOGGER.warn('Validation:%s' % self.validated)

    def render(self):
        """ We tell BulkSMS all is OK, unless something bad happens, like the
            Unauthorized we raise.  You will notice that we do this even if we
            cannot find the order or the validation of the auth tokens fails.
            This is necessary, because when one configures the MO delivery URL
            through the BulkSMS webpage, they check the URL immediately. If we
            don't return '200 OK' the config fails and the URL is rejected.

            You will also notice that we always return some text even if the 
            order is not found. This is again due to the fact that BulkSMS
            wants at least some text (204 is not acceptable).

            For more information see:
                https://bulksms.2way.co.za/docs/eapi/reception/http_push/
        """
        self.request.response.setStatus(200, 'OK')

        if self.order:
            if self.validated:
                return 'Order %s is now paid.' % self.order.getId()
            else:
                raise Unauthorized()
        else:
            return 'OK'
    
    def getOrder(self, context, request):
        """ This turns a little complex, because the call from BulkSMS is 
            unauthenticated in the plone sense. Thus this code essentially runs
            as 'Anonymous'. We do an unrestrictedSearchResults to get the brain.
            Then we switch users to the owner of that object. This means we
            never give the user more rights on this object than they should
            have.
        """
        verification_code = request.get('message')
        if not verification_code:
            return None
        
        pmt = getToolByName(self.context, 'portal_membership')
        admin = pmt.getMemberById(ADMIN_USER_ID)
        newSecurityManager(request, admin)
        pc = getToolByName(self.context, 'order_catalog')
        query = {'portal_type':       'emas.app.order',
                 'verification_code': verification_code}
        brains = pc.unrestrictedSearchResults(query)
        if not brains or len(brains) < 1:
            LOGGER.debug(
                'Could not find order with verification code:'
                '%s' % verification_code)
            return None
        
        brain = brains[0]
        order = brain.getObject()
        user = pmt.getMemberById(order.userid)
        newSecurityManager(request, user)
        return order

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
        """ Sender msisdn must be in international dialing format.
            eg. for traditional CellC numbers: 2784nnnnnnn or
            +2784nnnnnnn.
            The '+' is optional for BulkSMS.
        """
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

    def logRequest(self, request):
        keys = ['msisdn',
                'sender',
                'message',
                'dca',
                'msg_id',
                'source_id',
                'referring_batch_id',
                'referring_msg_id',
                'network_id',
                'concat_reference',
                'concat_num_segments',
                'concat_seq_num',
                'received_time',]
        for key in keys:
            LOGGER.info('Request:%s=%s' % (key, request.get(key)))
