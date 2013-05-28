import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from emas.app.service import IService
from emas.app.tests.base import INTEGRATION_TESTING


class TestServiceIntegration(unittest.TestCase):
    """Unit test for the service type
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'testfolder')
        self.folder = self.portal.testfolder
    
    def test_adding(self):
        s_id= self.folder.invokeFactory('emas.app.service',
                                        'service1',
                                        service_type='subscription',
                                        grade='12',
                                        subject='maths',
                                        price='111')
        s1 = self.folder._getOb(s_id)
        self.failUnless(IService.providedBy(s1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.service')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.service')
        schema = fti.lookupSchema()
        self.assertEquals(IService, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.service')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IService.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
