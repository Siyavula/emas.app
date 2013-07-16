import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI

from emas.app.tests.base import INTEGRATION_TESTING

from emas.app.order import IOrder


class TestOrder(unittest.TestCase):
    """Unit test for the Order type
    """
    
    def test_one(self):
        pass


class TestOrderIntegration(unittest.TestCase):
    
    layer = INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.orders

    def test_adding(self):
        self.folder.invokeFactory('emas.app.order', 'order1')
        order1 = self.folder['order1']
        self.failUnless(IOrder.providedBy(order1))
    
    def test_emas_catalogtool(self):
        self.folder.invokeFactory('emas.app.order', 'order1')
        order1 = self.folder['order1']
        oc = getToolByName(self.portal, 'order_catalog')
        query = {'portal_type': 'emas.app.order'}
        brains = oc(query)
        self.assertEqual(len(brains), 1,
                         'There should be only one order in the catalog.')
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.order')
        self.assertNotEquals(None, fti)
    
    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.order')
        schema = fti.lookupSchema()
        self.assertEquals(IOrder, schema)
    
    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.order')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IOrder.providedBy(new_object))
    
    def _test_view(self):
        self.folder.invokeFactory('emas.app.order', 'order')
        order1 = self.folder['order']
        view = order1.restrictedTraverse('@@view')
    

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

