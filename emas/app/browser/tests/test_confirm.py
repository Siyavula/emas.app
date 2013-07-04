import unittest
from types import StringType

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

POST_DATA = {
    'prod_payment': 'eft',
    'grade': 'grade10',
    'prod_practice_book': 'Practice,Textbook',
    'subjects': 'maths',
    'order.form.submitted': 'submitted',
    'fullname': 'Test user',
    'phone': '+27218888888',
    'shipping_address': '111 1st Avenue, Townsville, 9999',
}

class TestConfirmView(PloneTestCase):
    
    layer = Layer
    
    def test_confirm_view_exists(self):
        view = self.portal.restrictedTraverse('@@confirm')
        assert view is not None, '@@confirm view is missing.'

    def test_generate_verification_code(self):
        view = self.new_confirm_view()

        self.assertEqual(len(view.order.verification_code), 5,
                         'Verification code is too long.')

        assert(isinstance(view.order.verification_code, StringType),
               'Verification code must be a string.')


    def test_validate_non_unique_verification_code(self):
        view = self.new_confirm_view()
        vcode = '12345'
        view.order.verification_code = vcode
        view.order.reindexObject(idxs=['verification_code'])

        self.assertEqual(view.is_unique_verification_code(vcode), False,
                         'The verification code CANNOT be unique.')

    def test_validate_unique_verification_code(self):
        view = self.new_confirm_view()
        vcode = view.order.verification_code

        pc = getToolByName(self.portal, 'order_catalog')
        query = {'portal_type':       'emas.app.order',
                 'verification_code': vcode}
        brains = pc.unrestrictedSearchResults(query)

        self.assertEqual(len(brains), 1,
                         'The verification code SHOULD be unique.')

    def test_generate_verification_code_retries_exceeded(self):
        view = self.new_confirm_view()
        view.retries = 0

        with self.assertRaises(Exception) as context_manager:
            view.generate_verification_code(view.order)
        assert (isinstance(context_manager.exception, Exception),
                'Expected and error to occur when retry count is exceeded.')

    def test_practice_and_textbook_bought(self):
        """ This tests what happens in when the correct data is submitted as
            POST parameters to the view.

            We buy a textbook and practice for maths grade10.
        """
        pps = self.portal.restrictedTraverse('@@plone_portal_state')
        member = pps.member()
        member.setProperties(email='tester@example.com')

        view = self.portal.restrictedTraverse('@@confirm')
        view.request.form.update(POST_DATA)
        view.update()

        # verify the display items
        self.verify_display_items(view)

        # verify the discount items
        self.verify_discount_items(view)
    
        # verify the selected items
        self.verify_selected_items(view)

    def test_practice_and_textbook_bought_via_sms(self):
        """ Buy textbook and practice service.
            Pay via SMS.
        """
        pps = self.portal.restrictedTraverse('@@plone_portal_state')
        member = pps.member()
        member.setProperties(email='tester@example.com')

        post_data = POST_DATA
        post_data['prod_payment'] = 'sms'

        view = self.portal.restrictedTraverse('@@confirm')
        view.request.form.update(post_data)
        view.update()

    def verify_display_items(self, view):
        practice = self.portal.products_and_services['maths-grade10-practice']
        textbook = self.portal.products_and_services['maths-grade10-textbook']
        expected_items = {practice: 1,
                          textbook: 1,}
        self.assertEqual(view.display_items,
                         expected_items,
                         'Mismatch between expected and actual display items.')
        
    def verify_discount_items(self, view):
        discount = self.portal.products_and_services['maths-grade10-discount']
        expected_items = {discount: 1}
        self.assertEqual(view.discount_items,
                         expected_items,
                         'Mismatch between expected and actual discount items.')

    def verify_selected_items(self, view):
        practice = self.portal.products_and_services['maths-grade10-practice']
        textbook = self.portal.products_and_services['maths-grade10-textbook']
        discount = self.portal.products_and_services['maths-grade10-discount']
        expected_items = {practice: 1,
                          textbook: 1,
                          discount: 1}
        self.assertEqual(view.selected_items,
                         expected_items,
                         'Mismatch between expected and actual selected items.')

        # verify order details (attribs, ownership, etc.)

        # verify order items (attribs, ownership, quantity, etc.)
        
        # verify email was sent

        # verify email content

        # verify payment method

        # verify payment details

    def createOrder(self):
        pps = self.portal.restrictedTraverse('@@plone_portal_state')
        member = pps.member()
        member.setProperties(email='tester@example.com')
        view = self.portal.restrictedTraverse('@@confirm')
        post_data = POST_DATA
        post_data['prod_payment'] = 'sms'
        view.request.form.update(post_data)
        view.update()
        return view.order
    
    def new_confirm_view(self):
        pps = self.portal.restrictedTraverse('@@plone_portal_state')
        member = pps.member()
        member.setProperties(email='tester@example.com')
        view = self.portal.restrictedTraverse('@@confirm')
        post_data = POST_DATA
        post_data['prod_payment'] = 'sms'
        view.request.form.update(post_data)
        view.update()
        return view

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
