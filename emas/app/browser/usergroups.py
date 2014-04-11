from Acquisition import aq_inner
from zExceptions import Forbidden

from zope.component import getUtility

from plone.app.controlpanel.usergroups import UsersOverviewControlPanel as Base

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin

from emas.app.usercatalog import IUserCatalog

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

    def doSearch(self, searchString):
        acl = getToolByName(self, 'acl_users')
        mtool = getToolByName(self.context, 'portal_membership')
        rolemakers = acl.plugins.listPlugins(IRolesPlugin)
        usercatalog = getUtility(IUserCatalog)

        users = usercatalog.search(searchstring=searchString)
        
        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not
        # assigned at all (None).
        results = []
        for usermd in users:
            user = mtool.getMemberById(usermd['username'])
            userId = user.getMemberId()
            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                explicitlyAssignedRoles.extend(
                    rolemaker.getRolesForPrincipal(user)
                    )

            roleList = {}
            for role in self.portal_roles:
                canAssign = user.canAssignRole(role)
                if role == 'Manager' and not self.is_zope_manager:
                    canAssign = False
                roleList[role]={'canAssign': canAssign,
                                'explicit': role in explicitlyAssignedRoles,
                                'inherited': False}

            canDelete = user.canDelete()
            canPasswordSet = user.canPasswordSet()
            if roleList['Manager']['explicit'] or roleList['Manager']['inherited']:
                if not self.is_zope_manager:
                    canDelete = False
                    canPasswordSet = False

            user_info = {}
            user_info['userid'] = userId
            user_info['principal_type'] = 'user'
            user_info['title'] = userId
            user_info['roles'] = roleList
            user_info['fullname'] = user.getProperty('fullname', '')
            user_info['email'] = user.getProperty('email', '')
            user_info['can_delete'] = canDelete
            user_info['can_set_email'] = user.canWriteProperty('email')
            user_info['can_set_password'] = canPasswordSet
            results.append(user_info)

        # Sort the users by fullname
        results.sort(key=lambda x: x is not None and x['fullname'] is not None and normalizeString(x['fullname']) or '')

        return results

