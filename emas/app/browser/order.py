from five import grok
from zope.interface import Interface

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings

grok.templatedir('templates')

class Order(grok.View):
    """ Order form.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    def products_and_services(self):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        products_and_services = pps.portal()._getOb('products_and_services')
        return products_and_services.getFolderContents(full_objects=True)

    def action(self, isAnon):
        url = '%s/@@confirm' %self.context.absolute_url()
        if isAnon:
            url = '%s/@@order' %self.context.absolute_url()
        return url
