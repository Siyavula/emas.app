from Acquisition import aq_inner
from zExceptions import Forbidden

from zope.component import getUtility

from plone.app.controlpanel.usergroups import UsersOverviewControlPanel as Base

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


class UsersOverviewControlPanel(Base):
    """ Patch to not delete local roles, but delete member services
    """

    def deleteMembers(self, member_ids):
        # this method exists to bypass the 'Manage Users' permission check
        # in the CMF member tool's version
        context = aq_inner(self.context)
        mtool = getToolByName(self.context, 'portal_membership')

        # Delete members in acl_users.
        acl_users = context.acl_users
        if isinstance(member_ids, basestring):
            member_ids = (member_ids,)
        member_ids = list(member_ids)
        for member_id in member_ids[:]:
            member = mtool.getMemberById(member_id)
            if member is None:
                member_ids.remove(member_id)
            else:
                if not member.canDelete():
                    raise Forbidden
                if 'Manager' in member.getRoles() and not self.is_zope_manager:
                    raise Forbidden
        try:
            acl_users.userFolderDelUsers(member_ids)
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('The underlying User Folder '
                                     'doesn\'t support deleting members.')

        # Delete member data in portal_memberdata.
        mdtool = getToolByName(context, 'portal_memberdata', None)
        if mdtool is not None:
            for member_id in member_ids:
                mdtool.deleteMemberData(member_id)

        # Delete member services    
        query = {'portal_type': 'emas.app.memberservice',
                 'userid': member_id,
                }
        pc = getToolByName(context, 'portal_catalog')
        for brain in pc(query):
            obj = brain.getObject()
            obj.aq_parent.manage_delObjects(ids=obj.getId())
