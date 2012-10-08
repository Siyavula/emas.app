import unittest

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from emas.theme.interfaces import IEmasSettings

from Products.PloneTestCase.ptc import PloneTestCase

from emas.app.tests.layer import Layer

from emas.app.browser.tests.test_confirm import POST_DATA

class TestSMSPaymentApprovedView(PloneTestCase):
    
    layer = Layer

    def test_confirm_view_exists(self):
        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        assert view is not None, '@@smspaymentapproved view is missing.'

    def test_purchase_approved(self):
        order = self.createOrder()
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IEmasSettings)
        self.settings.bulksms_password = u'12345'
        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        view.request['password'] = self.settings.bulksms_password
        view.request['verification_code'] = order.verification_code
        result = view()
        
        self.assertEqual(result, 'OK')

        self.assertEqual(order, view.order, 'We found the wrong order!')

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

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
