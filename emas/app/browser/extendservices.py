import csv 
from cStringIO import StringIO

from five import grok
from plone.directives import form
from plone.namedfile.field import NamedFile
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.uuid.interfaces import IUUID

from zope import schema
from z3c.form import button
from z3c.relationfield.schema import RelationList, RelationChoice

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from emas.app.service import IService
from emas.app import MessageFactory as _

class IExtendMemberServices(form.Schema):
    """ Define form fields """

    csvfile = NamedFile(title=u"CVS File")

    services = RelationList(
        title=u'Services to extend',
        value_type=RelationChoice(
            title=_(u"Services to extend"),
            source=ObjPathSourceBinder(
                object_provides=IService.__identifier__
                )
            ),
        required=True,
    )

    expiry_date = schema.Date(title=u"Expiry Date")

class ExtendMemberServicesForm(form.SchemaForm):
    """ 
    """
    grok.name('extend-member-services')
    grok.require('cmf.ManagePortal')
    grok.context(ISiteRoot)

    schema = IExtendMemberServices
    ignoreContext = True

    @button.buttonAndHandler(u'Submit')
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        memberservices = portal['memberservices']
        ms_path = '/'.join(memberservices.getPhysicalPath())
        pc = getToolByName(portal, 'portal_catalog')

        file = StringIO(data['csvfile'].data)
        for row in csv.reader(file):
            if len(row) == 0:
                continue
            userid = row[0]
            for service in data['services']:
                uuid = IUUID(service)
                query = {'portal_type': 'emas.app.memberservice',
                         'userid': userid,
                         'path': ms_path,
                         'serviceuid': uuid}
                for brain in pc(query):
                    memberservice = brain.getObject()
                    memberservice.expiry_date = data['expiry_date']
                    memberservice.reindexObject()
                
        self.status = "Member services extended successfully"
