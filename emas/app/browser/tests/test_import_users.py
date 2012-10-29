import os
import csv
from cStringIO import StringIO
import unittest

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

dirname = os.path.dirname(__file__)

class TestImportUsersView(PloneTestCase):
    
    layer = Layer
    
    def setUp(self):
        super(TestImportUsersView, self).setUp()
        self.logout()
        self.loginAsPortalOwner()

    def test_view_exists(self):
        view = self.portal.restrictedTraverse('@@import-users')
        assert view is not None, '@@import-users view is missing.'

    def test_extractData_no_data(self):
        view = self.portal.restrictedTraverse('@@import-users')
        data = open(os.path.join(dirname, 'empty.csv'), 'rb')
        view.request.form['userdata'] = data
        errors, data = view.extractData(view.request)

        self.assertEqual(errors, ['No data supplied'],
                         'No errors returned.')

    def test_extractData(self):
        view = self.portal.restrictedTraverse('@@import-users')
        data = open(os.path.join(dirname, 'userimport.csv'), 'rb')
        view.request.form['userdata'] = data
        errors, data = view.extractData(view.request)

        self.assertEqual(errors, [],
                         'There should not be any errors')

    def test_imported_users(self):
        view = self.portal.restrictedTraverse('@@import-users')
        with open(os.path.join(dirname, 'userimport.csv'), 'rb') as data:
            view.request.form['userdata'] = data
            errors, data = view.extractData(view.request)

    def test_get_existing_users(self):
        view = self.portal.restrictedTraverse('@@import-users')
        pmt = getToolByName(view.context, 'portal_membership')
        with open(os.path.join(dirname, 'existingusers.csv'), 'rb') as raw_data:
            reader = csv.DictReader(raw_data)
            ids = view.get_existing_users(reader, pmt)
        
        self.assertEqual(ids, set(['test_user_1_']),
                         'At least test_user_1_ should exist.')

    def test_get_existing_users_no_common_users(self):
        view = self.portal.restrictedTraverse('@@import-users')
        pmt = getToolByName(view.context, 'portal_membership')
        with open(os.path.join(dirname, 'userimport.csv'), 'rb') as raw_data:
            reader = csv.DictReader(raw_data)
            ids = view.get_existing_users(reader, pmt)
        
        self.assertEqual(ids, set([]),
                         'None of the to-be-imported users should exist yet.')

    def test_import_users_empty_file(self):
        view = self.portal.restrictedTraverse('@@import-users')
        pmt = getToolByName(view.context, 'portal_membership')
        with open(os.path.join(dirname, 'empty.csv'), 'rb') as raw_data:
            reader = csv.DictReader(raw_data)
            existing_users, new_users = view.import_users(reader, pmt)

        self.assertEqual(existing_users, [],
                         'No users should have been found.')
        self.assertEqual(new_users, [],
                         'No users should have been created.')

    def test_import_users_some_empty_lines(self):
        view = self.portal.restrictedTraverse('@@import-users')
        pmt = getToolByName(view.context, 'portal_membership')
        filename = os.path.join(dirname, 'userimport_some_empty_lines.csv')
        with open(filename, 'rb') as raw_data:
            reader = csv.DictReader(raw_data)
            reader = csv.DictReader(raw_data)
            errors, existing_users, new_users = view.import_users(reader, pmt)

        self.assertEqual(len(new_users), 5,
                         '5 users should have been created.')

        self.assertEqual(len(errors), 1,
                         'There should be at least one error.')

    def test_import_users(self):
        view = self.portal.restrictedTraverse('@@import-users')
        pmt = getToolByName(view.context, 'portal_membership')
        with open(os.path.join(dirname, 'userimport.csv'), 'rb') as raw_data:
            reader = csv.DictReader(raw_data)
            reader = csv.DictReader(raw_data)
            existing_users, new_users = view.import_users(reader, pmt)

        self.assertEqual(len(existing_users), 0,
                         'None or the users should exist yet.')

        self.assertEqual(len(new_users), 17,
                         '17 users should have been created.')
        
        for userid in new_users:
            user = pmt.getMemberById(userid)
            
            self.assertNotEqual(user, None,
                                'The user should have been created.')
            self.assertEqual(user.getRoles(), ['Member', 'Authenticated'],
                             'Incorrect roles asssigned.')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
