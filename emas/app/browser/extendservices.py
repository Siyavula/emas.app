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
from emas.app.browser.utils import all_member_services_for
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
        memberservices = portal['memberservices']
        ms_path = '/'.join(memberservices.getPhysicalPath())
        
        new_services = 0
        file = StringIO(data['csvfile'].data)
        services = data['services']
        for row in csv.reader(file):
            LOGGER.debug('Processing row:%s' %row)
            if len(row) == 0:
                continue
            userid = row[0]
            for service in services:
                LOGGER.debug('Checking service:%s' % service.title)
                uuid = IUUID(service)
                tmpservices = all_member_services_for(portal,
                                                      ms_path,
                                                      [uuid],
                                                      userid)

                # we did not find a memberservice for this combination of:
                # service uuid: userid, we create a new memberservice
                if len(tmpservices) == 0:
                    new_services += 1
                    mstitle = '%s for %s' % (service.title, userid)
                    LOGGER.debug('Creating member service:%s' % mstitle)

                    related_service = create_relation(service.getPhysicalPath())
                    props = {'title': mstitle,
                             'userid': userid,
                             'related_service': related_service,
                             'service_type': service.service_type
                             }

                    ms = createContentInContainer(
                        memberservices,
                        'emas.app.memberservice',
                        False,
                        **props
                    )

                    # give the order owner permissions on the new memberservice, or
                    # we wont' be able to find the memberservices for this user
                    ms.manage_setLocalRoles(userid, ('Owner',))
                    tmpservices.append(ms)

                for memberservice in tmpservices:
                    LOGGER.debug('Updating member service:%s' % memberservice.title)
                    memberservice.expiry_date = data['expiry_date']
                    memberservice.reindexObject()
                
        self.status = "Member services extended successfully"
