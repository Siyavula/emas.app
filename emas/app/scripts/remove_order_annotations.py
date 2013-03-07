import sys
import transaction
from Testing import makerequest
from AccessControl.SecurityManagement import newSecurityManager

from zope.annotation.interfaces import IAnnotations
from zope.app.component.hooks import setSite

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
annotations = IAnnotations(memberservices)
del annotations["plone.folder.ordered.order"]
del annotations["plone.folder.ordered.pos"]

orders = portal._getOb('orders')
annotations = IAnnotations(orders)
del annotations["plone.folder.ordered.order"]
del annotations["plone.folder.ordered.pos"]

transaction.commit()
