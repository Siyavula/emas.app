from five import grok

from zope.component import getUtility
from plone.dexterity.interfaces import IDexterityFTI

from emas.app.order import IOrder

grok.templatedir('templates')

class OrderDetails(grok.View):
    """
    """
    grok.context(IOrder)
    grok.require('zope2.View')

    def schema(self):
        fti = getUtility(IDexterityFTI, name='emas.app.order')
        schema = fti.lookupSchema() 
        return schema

    def formatDate(self, date):
        import pdb;pdb.set_trace()
        return date
