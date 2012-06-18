import hashlib

from five import grok
from Acquisition import aq_inner

from zope.component import queryUtility
from zope.interface import Interface
from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings


grok.templatedir('templates')


def vcs_hash(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


class PaymentDetails(grok.View):
    """
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    
    def update(self):
        """
        Set local variables for use in the template.
        """


        settings = queryUtility(IRegistry).forInterface(IEmasSettings)
        
        # becomes the action to which the page is posted.
        self.action=settings.vcs_url

        # terminal id; becomes p1 in the template
        self.vcs_terminal_id = settings.vcs_terminal_id

        # no orderid, no processing possible. So we raise an error.
        # becomes p2 in the template
        self.tid = self.request.get('orderid')
        if self.tid == None or len(self.tid) < 1:
            raise AttributeError('No orderid supplied')

        order = self.getOrder(self.tid)
        # becomes p3 in the template
        self.description = 'Siyavula EMAS %s' %order.Title()
        
        # becomes p4 in the template
        self.cost = order.total()
        self.quantity = 1

        self.md5key = settings.vcs_md5_key

        self.md5hash = vcs_hash(self.vcs_terminal_id + self.tid + 
                                self.description + str(self.cost) +
                                self.md5key)

    def getOrder(self, orderid):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        portal = pps.portal()
        orders = portal._getOb('orders')
        return orders._getOb(orderid)

