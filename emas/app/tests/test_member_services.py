import unittest2 as unittest

from z3c.relationfield.relation import create_relation
from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from emas.app.member_service import IMemberService
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
        related_service = create_relation(self.service.getPhysicalPath())
        ms_id = self.folder.invokeFactory('emas.app.memberservice',
                                          'memberservice1',
                                          userid=TEST_USER_ID,
                                          related_service=related_service,
                                          service_type='subscription')
        ms1 = self.folder._getOb(ms_id)
        self.failUnless(IMemberService.providedBy(ms1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.memberservice')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.memberservice')
        schema = fti.lookupSchema()
        self.assertEquals(IMemberService, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.memberservice')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IMemberService.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
