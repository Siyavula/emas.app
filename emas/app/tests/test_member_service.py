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
        service1 = self.services['science-grade12-monthly-practice']
        ms1 = self.createMemberService(service1)
        service2 = self.services['science-grade12-practice']
        ms2 = self.createMemberService(service2)
        ms1 = ms1.merge_with(ms2)
        self.assertEquals(ms1.related_service, ms2.related_service,
                          'The related services should be the same.')

    def test_merge_memberservices_with_only_one_memberservice(self):
        memberservices = []
        ids = ['science-grade12-monthly-practice',]
        for id in ids:
            service = self.services[id]
            ms = self.createMemberService(service)
            memberservices.append(ms)
        memberservices = memberservices[0].merge_memberservices(memberservices)
        self.assertEquals(len(memberservices), 1,
                          'There should be just one memberservices left.')

    def test_merge_memberservices_only_science(self):
        memberservices = []
        ids = ['science-grade12-monthly-practice',
               'science-grade12-practice']
        for id in ids:
            service = self.services[id]
            ms = self.createMemberService(service)
            memberservices.append(ms)
        memberservices = memberservices[0].merge_memberservices(memberservices)
        self.assertEquals(len(memberservices), 1,
                          'There should be just one memberservices left.')
    
    def test_merge_memberservices_maths_and_science(self):
        memberservices = []
        ids = ['science-grade12-monthly-practice',
               'science-grade12-practice',
               'maths-grade12-monthly-practice',
               'maths-grade12-practice']
        for id in ids:
            service = self.services[id]
            ms = self.createMemberService(service)
            memberservices.append(ms)
        memberservices = memberservices[0].merge_memberservices(memberservices)
        self.assertEquals(len(memberservices), 4,
                          'There should be 4 memberservices.')
        self.assertEquals(memberservices[0].related_service,
                          memberservices[1].related_service,
                          'They should have the same related_service.')
        self.assertEquals(memberservices[2].related_service,
                          memberservices[3].related_service,
                          'They should have the same related_service.')
    
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
