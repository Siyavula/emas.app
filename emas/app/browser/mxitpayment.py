from urllib import urlencode
from five import grok
from Acquisition import aq_inner

from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings


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
        self.base_url = self.context.absolute_url()
        return

    def get_url(self):
        return self.base_url + '/papers'
