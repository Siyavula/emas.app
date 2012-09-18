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
from z3c.relationfield.relation import create_relation
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID

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

today = datetime.datetime.today().date()
products_and_services = portal._getOb('products_and_services')
memberservices = portal._getOb('memberservices')

now = datetime.datetime.utcnow()
pms = getToolByName(portal, 'portal_membership')
pc = getToolByName(portal, 'portal_catalog')

for member in members:
    practice_expirydate = member.getProperty('moreexercise_expirydate')
    intelligent_practice_access = member.getProperty(        
        'intelligent_practice_access')

    if practice_expirydate > today and len(intelligent_practice_access) > 0:

        print "Migrating services for %s." % member.getId()

        for grade_subject in intelligent_practice_access:
            subject, x, grade = grade_subject.split('-')
            sid = '%s-grade%s-practice' % (subject, grade)
            service = products_and_services[sid]
            service_relation = create_relation(service.getPhysicalPath())
            mstitle = '%s for %s' % (service.title, member.getId())

            query = {'portal_type': 'emas.app.memberservice',
                     'userid': member.getId(),
                     'serviceuid': IUUID(service),
                    }
            if len(pc(query)) > 0:
                continue

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
