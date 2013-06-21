from datetime import datetime, timedelta

import unittest2 as unittest
import transaction

from z3c.relationfield.relation import create_relation
from zope.component import createObject
from zope.component import queryUtility
from plone.dexterity.utils import createContentInContainer

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from emas.app.tests.base import INTEGRATION_TESTING


class TestMemberServiceIntegration(unittest.TestCase):
    """Unit test for the MemberService type
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.services = self.portal._getOb('products_and_services')
        self.science_services = \
            [s for s in self.services.objectValues() if s.subject == 'science']
        self.memberservices = self.portal._getOb('memberservices')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def test_is_enabled(self):
        self.fail()

    def test_is_similar_to(self):
        service1 = self.services['science-grade12-monthly-practice']
        ms1 = self.createMemberService(service1)
        service2 = self.services['science-grade12-practice']
        ms2 = self.createMemberService(service2)
        self.assertEquals(ms1.is_similar_to(ms2), True,
                          'The 2 should be similar.')

    def test_merge_with(self):
        self.fail()

    def test_merge_memberservices(self):
        self.fail()
    
    def createMemberService(self, service):
        mstitle = '%s for %s' % (service.title, TEST_USER_ID)
        related_service = create_relation(service.getPhysicalPath())
        props = {'title': mstitle,
                 'userid': TEST_USER_ID,
                 'related_service': related_service,
                 'service_type': service.service_type
                 }
        ms = createContentInContainer(
            self.memberservices,
            'emas.app.memberservice',
            False,
            **props
        )
        ms.manage_setLocalRoles(TEST_USER_ID, ('Owner',))
        now = datetime.now().date()
        ms.expiry_date = now + timedelta(service.subscription_period)
        return ms

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
