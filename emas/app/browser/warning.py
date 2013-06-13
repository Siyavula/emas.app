from five import grok
from Acquisition import aq_inner

from zope.interface import Interface

from emas.app.browser.utils import practice_service_uuids
from emas.app.browser.utils import service_url as get_service_url
from emas.app.memberservice import member_services
    
grok.templatedir('templates')
    
    
class Warning(grok.View):
    """ Display warnings about purchase/ payment errors.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    def update(self):
        uids = practice_service_uuids(self.context)
        self.memberservices =  member_services(self.context, uids)
        # grab any errors from the request, just in case we want to display
        # them later.
        self.errors = self.request.get('errors', [])

    def service_url(self, service):
        return get_service_url(service)
