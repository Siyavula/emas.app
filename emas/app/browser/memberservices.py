from five import grok
from Acquisition import aq_inner

from zope.interface import Interface

    
grok.templatedir('templates')
    
    
class MemberServices(grok.View):
    """
        Returns all the current authenticated member's services
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('member-services')

    def render(self):
        return ''
    
    def list_services(self):
        portal_state = self.context.restrictedTraverse('@@plone_portal_state')
        # get the services and products folder
        items_folder = portal_state.portal()._getOb('products_and_services')
        if items_folder is None:
            raise AttributeError('No products_and_services folder found.')
        return items_folder.getFolderContents(full_objects=True)
