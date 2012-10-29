import os
import csv
from cStringIO import StringIO
import unittest

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

dirname = os.path.dirname(__file__)

class TestExtendMemberServicesView(PloneTestCase):
    
    layer = Layer
    
    def test_view_exists(self):
        view = self.portal.restrictedTraverse('@@extend-member-services')
        assert view is not None, '@@extend-member-services view is missing.'
    
    def test_handleSubmit_nodata(self):
        self.portal.REQUEST["form.widgets.csvfile"] = ''
        self.portal.REQUEST["form.widgets.services"] = []
        self.portal.REQUEST["form.buttons.Submit"] = u"Submit"
        view = self.portal.restrictedTraverse('@@extend-member-services')

        view.process_form()
        print view.form.render()

        errors = view.errors
        self.assertEqual(len(errors), 0, "Got errors:" + str(errors))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
