from urllib import urlencode
from five import grok
from Acquisition import aq_inner

from zope.interface import Interface

    
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
        self.transaction_reference = '1'
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

    def render(self):
        return ''

    def update(self):
        import pdb;pdb.set_trace()
        return
