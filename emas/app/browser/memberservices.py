from five import grok

from zope.interface import Interface

from emas.app.browser.utils import practice_service_uuids
from emas.app.browser.utils import service_url as get_service_url
from emas.app.memberservice import MemberServicesDataAccess


grok.templatedir('templates')

class MemberServices(grok.View):
    """ Returns all the authenticated member's services
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('db-member-services')

    def update(self):
        self.service_uids = practice_service_uuids(self.context)
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        memberid = pps.member().getId()
        self.dao = MemberServicesDataAccess(self.context)
        self.memberservices = []
        self.memberservices = \
            self.dao.get_member_services(self.service_uids, memberid)

    def service_url(self, service):
        return ''

"""
class ActiveMemberServicesFor(grok.View):
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
"""
