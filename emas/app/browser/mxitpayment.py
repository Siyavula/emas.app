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
        self.action = 'http://billing.internal.mxit.com/Transaction/PaymentRequest'
        self.vendor_id = '1'
        self.transaction_reference = '1'
        self.callback_url = self.context.absolute_url() + 'mxitpaymentresponse'
        self.product_id = 'test product'
        self.product_name = 'test product'
        self.product_description = 'test description'
        self.moola_amount = 1
        self.currency_amount = 1


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
