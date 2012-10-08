import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from emas.app.tests.layer import Layer

from emas.app.order import IOrder

class TestConfirmView(PloneTestCase):
    
    layer = Layer
    
    def test_confirm_view_exists(self):
        view = self.portal.restrictedTraverse('@@confirm')
        assert view is not None, '@@confirm view is missing.'

    def test_nothing_bought(self):
        """ This tests what happens in update when the view is called the 
            first time. At that point nothing is submitted as POST data to the
            view and the result should really just be a empte confirmation
            page.

            In reality this should not even happen.
        """
        view = self.portal.restrictedTraverse('@@confirm')
        view.update()

    def test_practice_and_textbook_bought(self):
        """ This tests what happens in when the correct data is submitted as
            POST parameters to the view.

            We buy a textbook and practice for maths grade10.
        """
        pps = self.portal.restrictedTraverse('@@plone_portal_state')
        member = pps.member()
        member.setProperties(email='tester@example.com')

        post_data = {
            'grade': 'grade10',
            'prod_practice_book': 'Practice,Textbook',
            'subjects': 'maths',
            'order.form.submitted': 'submitted',
            'fullname': 'Test user',
            'phone': '+27218888888',
            'shipping_address': '111 1st Avenue, Townsville, 9999',
        }

        view = self.portal.restrictedTraverse('@@confirm')
        view.request.form.update(post_data)
        view.update()

        # verify the display items
        self.verify_display_items(view)

        # verify the discount items
        self.verify_discount_items(view)
    
        # verify the selected items
        self.verify_selected_items(view)

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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
