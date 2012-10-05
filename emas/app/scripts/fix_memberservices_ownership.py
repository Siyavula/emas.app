""" 
"""
import sys
import datetime
import transaction
from Testing import makerequest
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

from zope.app.component.hooks import setSite
from plone.uuid.interfaces import IUUID

from emas.theme.interfaces import IEmasSettings
from emas.app.member_service import IMemberService

try:
    portal_id = sys.argv[1]
except IndexError:
    portal_id = 'Plone' 

if not app.hasObject(portal_id):
    print "Please specify the id of your plone site as the first argument "
    print "to this script."
    print "Usage: <instancehome>/bin/instance run %s <id>" % sys.argv[0]
    sys.exit(1)

portal = app[portal_id]
setSite(portal)

# we assume there is an admin user
app = makerequest.makerequest(app)
user = app.acl_users.getUser('admin')
newSecurityManager(None, user.__of__(app.acl_users))

memberservices = portal._getOb('memberservices')

pms = getToolByName(portal, 'portal_membership')
pc = getToolByName(portal, 'portal_catalog')

count = 0

for ms in memberservices.objectValues():
    if not IMemberService.providedBy(ms):
        continue

    if ms.userid not in ms.users_with_local_role('Owner'):
        pms.setLocalRoles(ms, [ms.userid], 'Owner')
        ms.reindexObject()
        print "Fixing local roles for %s" % ms.getId()

transaction.commit()
