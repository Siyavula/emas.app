import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

from emas.app.order import IOrder


class TestOrder(unittest.TestCase):
    """Unit test for the Order type
    """
    
    def test_one(self):
        pass


class TestOrderIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('emas.app.order', 'order1')
        order1 = self.folder['order1']
        self.failUnless(IOrder.providedBy(order1))
    
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
    
    def test_equals(self):
        self.folder.invokeFactory('emas.app.order', 'order1')
        order1 = self.folder['order1']
        self.folder.invokeFactory('emas.app.order', 'order2')
        order2 = self.folder['order2']
        print order1 == order2
        self.assertEqual(order1, order2)
    

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

