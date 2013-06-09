from datetime import datetime

import unittest2 as unittest

from z3c.relationfield.relation import create_relation
from zope.component import createObject
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from emas.app.member_service import IMemberService
from emas.app.browser import utils
from emas.app.tests.base import INTEGRATION_TESTING


class TestMemberServiceIntegration(unittest.TestCase):
    """Unit test for the MemberService type
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'testfolder')
        self.folder = self.portal.testfolder
        s_id= self.folder.invokeFactory('emas.app.service',
                                        'service1',
                                        service_type='subscription',
                                        grade='12',
                                        subject='maths',
                                        price='111')
        self.service = self.folder._getOb(s_id)
    
    def test_adding(self):
        intids = queryUtility(IIntIds, context=self.portal)
        kwargs = {'memberid': TEST_USER_ID,
                  'title': '%s for %s' % (self.service.title, TEST_USER_ID),
                  'related_service_id': intids.getId(self.service),
                  'expiry_date': datetime.now(),}
        ms1= utils.add_memberservice(self.portal, **kwargs) 
        self.failUnless(IMemberService.providedBy(ms1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.memberservice')
        self.assertEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.memberservice')
        schema = fti.lookupSchema()
        self.assertEquals(None, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.memberservice')
        factory = fti.factory
        self.assertEquals(factory, None)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
