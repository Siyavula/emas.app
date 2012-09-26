from five import grok
from Acquisition import aq_inner

from zope.interface import Interface

from emas.app.browser.utils import practice_service_uuids
from emas.app.browser.utils import member_services
from emas.app.browser.utils import member_services_for
from emas.app.browser.utils import service_url as get_service_url
    
grok.templatedir('templates')
    
    
class MemberServices(grok.View):
    """ Returns all the authenticated member's services
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('member-services')

    def update(self):
        uids = practice_service_uuids(self.context)
        self.memberservices =  member_services(self.context, uids)

    def service_url(self, service):
        return get_service_url(service)

    
class ActiveMemberServicesFor(grok.View):
    """ Show all memberservices for a specific user.
        Used as administration reporting tool.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('active-memberservices-for')

    def update(self):
        self.memberservices = []
        self.userid = self.request.get('userid', '')
        if self.userid:
            uids = practice_service_uuids(self.context)
            self.memberservices =  member_services_for(self.context,
                                                       uids,
                                                       self.userid)

