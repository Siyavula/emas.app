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

ITEMS = {
    'maths-grade10-practice'   : {
        'title': 'Maths Grade 10 Intelligent Practice',
        'type': 'emas.app.service',
        'price': 150.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-10',
        'subject': u'maths'},

    'maths-grade11-practice'   : {
        'title': 'Maths Grade 11 Intelligent Practice',
        'type': 'emas.app.service',
        'price': 150.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-11',
        'subject': u'maths'},

    'maths-grade12-practice'   : {
        'title': 'Maths Grade 12 Intelligent Practice',
        'type': 'emas.app.service',
        'price': 150.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-12',
        'subject': u'maths'},

    'science-grade10-practice' : {
        'title': 'Science Grade 10 Intelligent Practice',
        'type': 'emas.app.service',
        'price': 150.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-10',
        'subject': u'science'},

    'science-grade11-practice' : {
        'title': 'Science Grade 11 Intelligent Practice',
        'type': 'emas.app.service',
        'price': 150.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-11',
        'subject': u'science'},

    'science-grade12-practice' : {
        'title': 'Science Grade 12 Intelligent Practice',
        'type': 'emas.app.service',
        'price': 150.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-12',
        'subject': u'science'},

    'maths-grade10-questions'  : {
        'title': 'Maths Grade 10 Expert Answer Service',
        'type': 'emas.app.service',
        'price': 10.00,
        'grade': u'grade-10',
        'service_type': 'credit',
        'amount_of_credits': 10,
        'access_path'  :'',
        'subject': u'maths'},

    'maths-grade11-questions'  : {
        'title': 'Maths Grade 11 Expert Answer Service',
        'type': 'emas.app.service',
        'price': 10.00,
        'grade': u'grade-11',
        'service_type': 'credit',
        'amount_of_credits': 10,
        'access_path'  :'',
        'subject': u'maths'},

    'maths-grade12-questions'  : {
        'title': 'Maths Grade 12 Expert Answer Service',
        'type': 'emas.app.service',
        'price': 10.00,
        'grade': u'grade-12',
        'service_type': 'credit',
        'amount_of_credits': 10,
        'access_path'  :'',
        'subject': u'maths'},

    'science-grade10-questions': {
        'title': 'Science Grade 10 Expert Answer Service',
        'type': 'emas.app.service',
        'price': 10.00,
        'grade': u'grade-10',
        'service_type': 'credit',
        'amount_of_credits': 10,
        'access_path'  :'',
        'subject': u'science'},

    'science-grade11-questions': {
        'title': 'Science Grade 11 Expert Answer Service',
        'type': 'emas.app.service',
        'price': 10.00,
        'grade': u'grade-11',
        'service_type': 'credit',
        'amount_of_credits': 10,
        'access_path'  :'',
        'subject': u'science'},

    'science-grade12-questions': {
        'title': 'Science Grade 12 Expert Answer Service',
        'type': 'emas.app.service',
        'price': 10.00,
        'grade': u'grade-12',
        'service_type': 'credit',
        'amount_of_credits': 10,
        'access_path'  :'',
        'subject': u'science'},

    'maths-grade10-textbook'  : {
        'title': 'Maths Grade 10 Textbook',
        'type': 'emas.app.service',
        'price': 95.00,
        'grade': u'grade-10',
        'service_type': 'credit',
        'amount_of_credits': 100,
        'subject': u'maths'},

    'maths-grade11-textbook'  : {
        'title': 'Maths Grade 11 Textbook',
        'type': 'emas.app.service',
        'price': 95.00,
        'grade': u'grade-11',
        'service_type': 'credit',
        'amount_of_credits': 100,
        'subject': u'maths'},

    'maths-grade12-textbook'  : {
        'title': 'Maths Grade 12 Textbook',
        'type': 'emas.app.service',
        'price': 95.00,
        'grade': u'grade-12',
        'service_type': 'credit',
        'amount_of_credits': 100,
        'subject': u'maths'},

    'science-grade10-textbook': {
        'title': 'Science Grade 10 Textbook',
        'type': 'emas.app.service',
        'price': 95.00,
        'grade': u'grade-10',
        'service_type': 'credit',
        'amount_of_credits': 100,
        'subject': u'science'},

    'science-grade11-textbook': {
        'title': 'Science Grade 11 Textbook',
        'type': 'emas.app.service',
        'price': 95.00,
        'grade': u'grade-11',
        'service_type': 'credit',
        'amount_of_credits': 100,
        'subject': u'science'},

    'science-grade12-textbook': {
        'title': 'Science Grade 12 Textbook',
        'type': 'emas.app.service',
        'price': 95.00,
        'grade': u'grade-12',
        'service_type': 'credit',
        'amount_of_credits': 100,
        'subject': u'science'},

    'maths-grade10-discount'   : {
        'title': 'Maths Grade 10 Discount',
        'type': 'emas.app.service',
        'price': -45.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'subject': u'maths'},

    'maths-grade11-discount'   : {
        'title': 'Maths Grade 11 Discount',
        'type': 'emas.app.service',
        'price': -45.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'subject': u'maths'},

    'maths-grade12-discount'   : {
        'title': 'Maths Grade 12 Discount',
        'type': 'emas.app.service',
        'price': -45.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'subject': u'maths'},

    'science-grade10-discount' : {
        'title': 'Science Grade 10 Discount',
        'type': 'emas.app.service',
        'price': -45.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'subject': u'science'},

    'science-grade11-discount' : {
        'title': 'Science Grade 11 Discount',
        'type': 'emas.app.service',
        'price': -45.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'subject': u'science'},

    'science-grade12-discount' : {
        'title': 'Science Grade 12 Discount',
        'type': 'emas.app.service',
        'price': -45.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'subject': u'science'},

    'maths-grade10-papers'   : {
        'title': 'Maths Grade 10 Papers',
        'type': 'emas.app.service',
        'price': 2.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'amount_of_moola': 200,
        'access_path'  :'maths/past-exam-papers/maths',
        'subject': u'maths'},

    'maths-grade11-papers'   : {
        'title': 'Maths Grade 11 Papers',
        'type': 'emas.app.service',
        'price': 2.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'amount_of_moola': 200,
        'access_path'  :'maths/past-exam-papers/maths',
        'subject': u'maths'},

    'maths-grade12-papers'   : {
        'title': 'Maths Grade 12 Papers',
        'type': 'emas.app.service',
        'price': 2.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 365,
        'channels': ['mxit', 'web', 'mobile'], 
        'access_group': 'PastMathsExamPapers',
        'amount_of_credits': 0,
        'amount_of_moola': 200,
        'access_path'  :'maths/past-exam-papers/maths',
        'subject': u'maths'},

    'science-grade10-papers' : {
        'title': 'Science Grade 10 Papers',
        'type': 'emas.app.service',
        'price': 2.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'amount_of_moola': 200,
        'access_path'  :'science/past-exam-papers/science',
        'subject': u'science'},

    'science-grade11-papers' : {
        'title': 'Science Grade 11 Papers',
        'type': 'emas.app.service',
        'price': 2.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 365,
        'amount_of_credits': 0,
        'amount_of_moola': 200,
        'access_path'  :'science/past-exam-papers/science',
        'subject': u'science'},

    'science-grade12-papers' : {
        'title': 'Science Grade 12 Papers',
        'type': 'emas.app.service',
        'price': 2.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 365,
        'channels': ['mxit', 'web', 'mobile'], 
        'access_group': 'PastScienceExamPapers',
        'amount_of_credits': 0,
        'amount_of_moola': 200,
        'access_path'  :'science/past-exam-papers/science',
        'subject': u'science'},

    'maths-grade10-monthly-practice'   : {
        'title': 'Maths Grade 10 Monthly Intelligent Practice',
        'type': 'emas.app.service',
        'price': 15.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 30,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-10',
        'subject': u'maths'},

    'maths-grade11-monthly-practice'   : {
        'title': 'Maths Grade 11 Monthly Intelligent Practice',
        'type': 'emas.app.service',
        'price': 15.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 30,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-11',
        'subject': u'maths'},

    'maths-grade12-monthly-practice'   : {
        'title': 'Maths Grade 12 Monthly Intelligent Practice',
        'type': 'emas.app.service',
        'price': 15.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 30,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-12',
        'subject': u'maths'},

    'science-grade10-monthly-practice' : {
        'title': 'Science Grade 10 Monthly Intelligent Practice',
        'type': 'emas.app.service',
        'price': 15.00,
        'grade': u'grade-10',
        'service_type': 'subscription',
        'subscription_period': 30,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-10',
        'subject': u'science'},

    'science-grade11-monthly-practice' : {
        'title': 'Science Grade 11 Monthly Intelligent Practice',
        'type': 'emas.app.service',
        'price': 15.00,
        'grade': u'grade-11',
        'service_type': 'subscription',
        'subscription_period': 30,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-11',
        'subject': u'science'},

    'science-grade12-monthly-practice' : {
        'title': 'Science Grade 12 Monthly Intelligent Practice',
        'type': 'emas.app.service',
        'price': 15.00,
        'grade': u'grade-12',
        'service_type': 'subscription',
        'subscription_period': 30,
        'amount_of_credits': 0,
        'access_path'  :'@@practice/grade-12',
        'subject': u'science'},

}


def setupPortalContent(portal):
    """
        We don't specify workflows for the emas.app containers, since there
        default workflow state is sufficient.
    """

    folders = [
        {'id': 'orders',
        'type': 'emas.app.orderfolder',
        'title': 'Orders',
        'exclude_from_nav':True,
        },
        {'id': 'products_and_services',
        'type': 'Folder',
        'title': 'Products and Services',
        'allowed_types': ['emas.app.product', 'emas.app.service'],
        'exclude_from_nav':True,
        'workflowid': 'simple_publication_workflow',
        'publish': True,
        },
        {'id': 'memberservices',
        'type': 'emas.app.memberservicefolder',
        'title': 'Member Services',
        'exclude_from_nav':True,
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

        # Nobody is allowed to modify the constraints or tweak the
        # display here
        folder.manage_permission(ModifyConstrainTypes, roles=[])
        folder.manage_permission(ModifyViewTemplate, roles=[])
        
        if folder_dict.get('publish', False):
            wf = getToolByName(portal, 'portal_workflow')
            wfid = folder_dict['workflowid']
            status = wf.getStatusOf(wfid, folder)
            if status and status['review_state'] != 'published':
                wf.doActionFor(folder, 'publish')
                folder.reindexObject()


def setupCatalogIndexes(portal):
    new_indexes = {
        'userid': 'FieldIndex',
        'serviceuid': 'FieldIndex',
        'grade': 'FieldIndex',
        'subject': 'FieldIndex',
        'expiry_date': 'DateIndex',
        'channels': 'FieldIndex',
        'verification_code': 'FieldIndex',
    }

    catalog = getToolByName(portal, 'portal_catalog')
    current_indexes = catalog.indexes()
    for name, type in new_indexes.items():
        if name not in current_indexes:
            catalog.addIndex(name, type)
            catalog.reindexIndex(name, {})


def setupProductsAndServices(portal):
    wf = getToolByName(portal, 'portal_workflow')
    products_and_services = portal._getOb('products_and_services')
    ids = products_and_services.objectIds()
    for key, values in ITEMS.items():
        if key in ids:
            continue
        
        products_and_services.invokeFactory(type_name=values['type'],
            id=key,
            **values
        ) 
        item = products_and_services._getOb(key)
        item.subject = values['subject']
        wf = getToolByName(portal, 'portal_workflow')
        status = wf.getStatusOf('simple_publication_workflow', item)
        if status and status['review_state'] != 'published':
            wf.doActionFor(item, 'publish')
            item.reindexObject()


def setupCustomCatalog(portal):
    if not portal.hasObject('order_catalog'):
        addTool = portal.manage_addProduct['emas.app'].manage_addTool
        # Add the tool by its meta_type
        addTool('EMAS Catalog Tool')

    catalog = portal.order_catalog
    
    new_indexes = {'review_state'        : 'FieldIndex',
                   'payment_method'      : 'FieldIndex',
                   'userid'              : 'FieldIndex',
                   'related_item_uuids'  : 'KeywordIndex',
                   'allowedRolesAndUsers': 'KeywordIndex',
                   'getId'               : 'FieldIndex',
                   'order_date'          : 'DateIndex',
                   'verification_code'   : 'FieldIndex',}

    current_indexes = catalog.indexes()
    for index_name, index_type in new_indexes.items():
        if not index_name in current_indexes:
            catalog.addIndex(index_name, index_type, extra=None)


def install(context):
    if context.readDataFile('emas.app-marker.txt') is None:
        return
    site = context.getSite()
    setupCustomCatalog(site)
    setupPortalContent(site)
    setupCatalogIndexes(site)
    setupProductsAndServices(site)
