import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

from emas.app.order import IOrder


class TestStateHashPerformance(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('emas.app.order', 'order1')
        order1 = self.folder['order1']
        self.failUnless(IOrder.providedBy(order1))
    

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
