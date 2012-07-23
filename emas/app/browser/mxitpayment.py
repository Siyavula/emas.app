from urllib import urlencode
from five import grok
from Acquisition import aq_inner

from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

from emas.theme.interfaces import IEmasSettings

from emas.app.browser.utils import compute_member_id
from emas.app.browser.utils import get_password_hash

    
MXIT_MESSAGES = {
    '0':
        u'Transaction completed successfully.',

    '1':
        u'Transaction rejected by user.',

    '2':
        u'Invalid MXit login name or password (authentication failure).',

    '3':
        u'User account is locked.',

    '4':
        u'User has insufficient funds.',

    '5':
        u'Transaction timed out before a response was received from the user.',

    '6': 
        u'The user logged out without confirming or rejecting the transaction.',

    '-2':
        u'The transaction parameters are not valid.',

    '-1':
        u'Technical system error occurred.',
}

grok.templatedir('templates')


class MxitPaymentRequest(grok.View):
    """
        Mxit payment processor.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('mxitpaymentrequest')
    
    def update(self):
        self.base_url = 'http://billing.internal.mxit.com/Transaction/PaymentRequest'
        self.action = self.context.absolute_url() + '/@@mxitpaymentrequest'
        self.vendor_id = '1'

        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)
        self.transaction_reference = self.settings.order_sequence_number + 1
        self.settings.order_sequence_number = self.transaction_reference
        self.transaction_reference = '%04d' % self.transaction_reference

        self.callback_url = self.context.absolute_url() + '/mxitpaymentresponse'
        self.product_id = 'test product'
        self.product_name = 'test product'
        self.product_description = 'test description'
        self.moola_amount = 1
        self.currency_amount = 1

    def get_url(self):
        query_dict = {
            "VendorId": self.vendor_id,
            "TransactionReference": self.transaction_reference,
            "CallbackUrl": self.callback_url,
            "ProductId": self.product_id,
            "ProductName": self.product_name,
            "ProductDescription": self.product_description,
            "MoolaAmount": self.moola_amount,
            "CurrencyAmount": self.currency_amount,
        }
        return self.base_url + '?' + urlencode(query_dict)


class MxitPaymentResponse(grok.View):
    """
        Mxit payment processor.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('mxitpaymentresponse')

    
    def update(self):
        """ Handle the mxit response
        """
        import pdb;pdb.set_trace()
        context = self.context
        request = self.request
        self.base_url = context.absolute_url()
        self.response_code = request.get('mxit_transaction_res', None)
        self.message = MXIT_MESSAGES.get(self.response_code, '')

        # check response code
        if not self.response_code:
            return
       
        # Transaction completed successfully.
        if self.response_code == '0':
            if request.has_key() and request.has_key():
                login = request.get('X-MXit-ID-R')
                internaluserid = request.get('X-MXit-USERID-R')
                memberid = compute_member_id(internaluserid)
                password = get_password_hash(login, internaluserid)

                pmt = getToolByName(context, 'portal_membership')
                member = pmt.getMemberId(memberid)
                if not member:
                    member = self.addMember(memberid, password, 'Member', '')
                
                # now add the member to the correct group


    def get_url(self):
        return self.base_url + '/papers'
