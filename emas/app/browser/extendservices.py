import csv 
import logging
import transaction
from cStringIO import StringIO

from five import grok
from plone.directives import form
from plone.namedfile.field import NamedFile
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.uuid.interfaces import IUUID
from plone.dexterity.utils import createContentInContainer

from zope import schema
from z3c.form import button
from z3c.relationfield.relation import create_relation
from z3c.relationfield.schema import RelationList, RelationChoice

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from emas.app.service import IService
from emas.app import MessageFactory as _

LOGGER = logging.getLogger('exendservices:')

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
        dao = MemberServicesDataAccess(portal) 
        new_services = 0
        file = StringIO(data['csvfile'].data)
        services = data['services']
        for row in csv.reader(file):
            LOGGER.debug('Processing row:%s' %row)
            if len(row) == 0:
                continue
            memberid = row[0]
            for service in services:
                LOGGER.debug('Checking service:%s' % service.title)
                intid = intids.getId(service)
                tempservices = dao.get_memberservices(memberid, [intid,])

                # we did not find a memberservice for this combination of:
                # service intid: memberid, we create a new memberservice
                if len(tmpservices) == 0:
                    new_services += 1
                    mstitle = '%s for %s' % (service.title, memberid)
                    LOGGER.debug('Creating member service:%s' % mstitle)

                    props = {'memberid': memberid,
                             'title': mstitle,
                             'related_service_id': intids.getId(related_service),
                             'expiry_date' : data['expiry_date'],
                             'service_type': service.service_type,
                            }
                    ms = dao.add_memberservice(**props)
                    tmpservices.append(ms)
                
        self.status = "Member services extended successfully"
