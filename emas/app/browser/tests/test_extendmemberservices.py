import os
import csv
from cStringIO import StringIO
import unittest

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

dirname = os.path.dirname(__file__)

class TestExtendMemberServicesView(PloneTestCase):
    
    layer = Layer
    
    def test_view_exists_nonmanager(self):
        with self.assertRaises(Unauthorized) as cm: 
            self.portal.restrictedTraverse('@@extend-member-services')

    def test_view_exists(self):
        self.setRoles('Manager')
        view = self.portal.restrictedTraverse('@@extend-member-services')
        assert view is not None, '@@extend-member-services view is missing.'
    
    def test_handleSubmit_nodata(self):
        self.setRoles('Manager')
        self.portal.REQUEST["form.widgets.csvfile"] = ''
        self.portal.REQUEST["form.widgets.services"] = []
        self.portal.REQUEST["form.buttons.Submit"] = u"Submit"
        view = self.portal.restrictedTraverse('@@extend-member-services')

        view.process_form()
        print view.form.render()

        errors = view.errors
        self.assertEqual(len(errors), 0, "Got errors:" + str(errors))

    def test_update_nonexistent_memberservices(self):
        self.setRoles('Manager')
        # grab some test data
        data = self._get_csv_data('nonexistentservices.csv')
        self.portal.REQUEST["form.widgets.csvfile"] = data
        self.portal.REQUEST["form.widgets.services"] = [
            'maths-grade10-practice',]
        self.portal.REQUEST["form.buttons.Submit"] = u"Submit"
        view = self.portal.restrictedTraverse('@@extend-member-services')
    
    def _get_csv_data(self, filename):
        os.path.join(dirname, filename)
        file = open(filename, 'rb')
        data = file.read() 
        file.close()
        return data


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
