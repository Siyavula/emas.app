import unittest

from ZPublisher import NotFound
from AccessControl import Unauthorized 
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from Products.PloneTestCase.ptc import PloneTestCase
from Products.CMFCore.utils import getToolByName

from emas.theme.interfaces import IEmasSettings
from emas.app.tests.layer import Layer
from emas.app.browser.tests.test_confirm import POST_DATA

class TestSMSPaymentApprovedView(PloneTestCase):
    
    layer = Layer

    def test_confirm_view_exists(self):
        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        assert view is not None, '@@smspaymentapproved view is missing.'

    def test_purchase_approved(self):
        order = self.createOrder()

        settings = self.getSettings()
        settings.bulksms_receive_password = u'12345'
        settings.bulksms_send_username = u'upfronttest'
        settings.bulksms_send_password = u'upfr0nt'
    
        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        view.request['password'] = settings.bulksms_receive_password
        view.request['message'] = order.verification_code
        view.request['sender'] = '27848051301'
        view()
        
        self.assertEqual(view.request.response.getStatus(),
                         200,
                         'Wrong status code was returned.')

        self.assertEqual(order, view.order, 'We found the wrong order!')
        
        wfs = self.getWorkflowState(view, view.order)
        self.assertEqual(wfs, 'paid', 'Order should be "paid" now.')

        # validate that we can now access the services with the current creds
        practice = self.portal.restrictedTraverse('@@practice')

    def test_purchase_approved_incorrect_password(self):
        order = self.createOrder()

        settings = self.getSettings()
        settings.bulksms_receive_password = u'12345'

        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        view.request['password'] = u''
        view.request['message'] = order.verification_code
        view.request['sender'] = '27848051301'

        with self.assertRaises(Unauthorized) as context_manager:
            view()
        assert (isinstance(context_manager.exception, Unauthorized),
                'Unauthorized exception expected.')
        
        wfs = self.getWorkflowState(view, view.order)
        self.assertEqual(wfs, 'ordered', 'Order should be in "ordered" state.')

    def test_purchase_approved_incorrect_verification_code(self):
        order = self.createOrder()

        settings = self.getSettings()
        settings.bulksms_receive_password = u'12345'

        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        view.request['password'] = settings.bulksms_receive_password
        view.request['message'] = ''
        view.request['sender'] = '27848051301'
        view()

        assert view.order == None, 'We should not find an order at all.'

    def test_purchase_approved_incorrect_sms_credentials(self):
        order = self.createOrder()

        settings = self.getSettings()
        settings.bulksms_send_username = u'test'
        settings.bulksms_send_password = u'12345'
        settings.bulksms_receive_password = u'12345'

        view = self.portal.restrictedTraverse('@@smspaymentapproved')
        view.request['password'] = settings.bulksms_receive_password
        view.request['message'] = order.verification_code
        view.request['sender'] = '27848051301'

        with self.assertRaises(Unauthorized) as context_manager:
            view()
        assert (isinstance(context_manager.exception, Unauthorized),
                'Unauthorized exception expected.')

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

    def getSettings(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IEmasSettings)
        return settings

    def getWorkflowState(self, context, order):
        wf = getToolByName(context, 'portal_workflow')
        status = wf.getStatusOf('order_workflow', order)
        return status['review_state']

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
