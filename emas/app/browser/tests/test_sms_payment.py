import unittest

from Products.PloneTestCase.ptc import PloneTestCase

from emas.app.tests.layer import Layer

class TestSMSPaymentApprovedView(PloneTestCase):
    
    layer = Layer
    
    def test_confirm_view_exists(self):
        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        assert view is not None, '@@smspaymentapproved view is missing.'

    def test_purchase_approved(self):
        self.fail('Not implemented yet.')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
