import logging
from StringIO import StringIO

import transaction
from zope.interface import directlyProvides, directlyProvidedBy

from Products.ATContentTypes.permission import ModifyConstrainTypes
from Products.ATContentTypes.permission import ModifyViewTemplate
from Products.ATContentTypes.lib.constraintypes import ENABLED
from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent, AddPortalContent
from Products.CMFCore.permissions import DeleteObjects

log = logging.getLogger('emas.app-setuphandlers')

DEFAULT_TYPES = ['Folder', 'Document']

def setupPortalContent(portal):
    folders = [
        {'id': 'orders',
        'type': 'Folder',
        'title': 'Orders',
        'allowed_types': ['emas.app.order'],
        'exclude_from_nav':True,
        'publish': False, 
        },
        {'id': 'products_and_services',
        'type': 'Folder',
        'title': 'Products and Services',
        'allowed_types': ['emas.app.product', 'emas.app.service'],
        'exclude_from_nav':True,
        'publish': True,
        },
        {'id': 'memberservices',
        'type': 'Folder',
        'title': 'Member Services',
        'allowed_types': ['emas.app.memberservice'],
        'exclude_from_nav':True,
        'publish': False,
        },
    ]

    for folder_dict in folders:
        if not portal.hasObject(folder_dict['id']):
            portal.invokeFactory(type_name=folder_dict['type'],
                id=folder_dict['id'],
                title=folder_dict['title'],
                exclude_from_nav=folder_dict.get('exclude_from_nav', False),
            ) 

        folder = portal._getOb(folder_dict['id'])

        #folder.setLayout(folder_dict['layout'])
        folder.setConstrainTypesMode(ENABLED)
        folder.setLocallyAllowedTypes(folder_dict['allowed_types'])
        folder.setImmediatelyAddableTypes(folder_dict['allowed_types'])
        # Nobody is allowed to modify the constraints or tweak the
        # display here
        folder.manage_permission(ModifyConstrainTypes, roles=[])
        folder.manage_permission(ModifyViewTemplate, roles=[])
        
        if folder_dict.get('publish', False):
            wf = getToolByName(portal, 'portal_workflow')
            status = wf.getStatusOf('simple_publication_workflow', folder)
            if status['review_state'] != 'published':
                wf.doActionFor(folder, 'publish')
                folder.reindexObject()


def setupCatalogIndexes(portal):
    new_indexes = {
        'userid': 'FieldIndex',
        'serviceuid': 'FieldIndex',
    }

    catalog = getToolByName(portal, 'portal_catalog')
    current_indexes = catalog.indexes()
    for name, type in new_indexes.items():
        if name not in current_indexes:
            catalog.addIndex(name, type)
            catalog.reindexIndex(name, {})


def install(context):
    if context.readDataFile('emas.app-marker.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)
    setupCatalogIndexes(site)


