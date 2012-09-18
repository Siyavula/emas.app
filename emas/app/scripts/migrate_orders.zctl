""" 
"""
import sys
import datetime
import transaction
from Testing import makerequest
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from z3c.relationfield.relation import create_relation

from zope.app.component.hooks import setSite

from emas.theme.interfaces import IEmasSettings

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

members = portal.portal_membership.listMembers()
print 'Preparing to update %s folders for members.' %len(members)

today = datetime.datetime.now()
products_and_services = portal._getOb('products_and_services')
memberservices = portal._getOb('memberservices')

now = datetime.datetime.utcnow()
pms = getToolByName(portal, 'portal_membership')
for member in members:
    print "Migrating services for:%s." % member.getId()

    practice_expirydate = getattr(member, 'moreexercise_expirydate')
    intelligent_practice_access = getattr(member, 'intelligent_practice_access')

    if practice_expirydate > today and len(intelligent_practice_access) > 0:

        for grade_subject in intelligent_practice_access:
            sid = '%s-practice' % grade_subject
            service = products_and_services[sid]
            service_relation = create_relation(service.getPhysicalPath())
            mstitle = '%s for %s' (service.title, member.getId())

            props = {'title': '%s for %s',
                     'userid': member.getId(),
                     'related_service': service_relation,
                     'service_type': service.service_type}

            ms = createContentInContainer(
                memberservices,
                'emas.app.memberservice',
                False,
                **props
            )
            ms.expiry_date = practice_expirydate
            ms.changeOwnership(member)
            ms.reindexObject()

transaction.commit()
