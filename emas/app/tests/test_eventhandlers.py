import unittest2 as unittest

from plone.testing.z2 import Browser as z2Browser
from zope.testbrowser.browser import Browser as ZopeTestBrowser

from emas.app.tests.base import FUNCTIONAL_TESTING 

class MemberServiceFunctionalTests(unittest.TestCase):

    layer =  FUNCTIONAL_TESTING

    def test_register(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        import pdb;pdb.set_trace()

        #browser = ZopeTestBrowser()
        #browser.open('http://nohost/plone/@@register')
        #browser.getControl('Full Name').value = 'tester086'
        #browser.getControl('E-mail').value = 'rijk@upfrontsystems.co.za'
        #browser.getControl('Confirm password').value = '12345'
        #browser.getControl('Subscibe to newsletter').selected = False
        #browser.getControl('Register').click()

        browser = z2Browser(self.app)
        browser.open(self.portal.portal_url() + '/register')
        assert('register' in browser.contents,
               'This is not the registration page.')

