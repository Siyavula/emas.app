import os
import csv
from cStringIO import StringIO
import unittest

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

dirname = os.path.dirname(__file__)

class TestVCSResponseProcessor(PloneTestCase):
    
    layer = Layer
    
    def test_errorhandling(self):
        view = self.portal.restrictedTraverse('@@paymentapproved')
        view.request['p2'] = '12345'
        result = view()
        import pdb;pdb.set_trace()
        print result

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
