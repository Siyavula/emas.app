import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

from emas.app.order import IOrder


class TestVCSPaymentIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_prepVCS(self):
        self.fail('Nothing tested yet.')
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
