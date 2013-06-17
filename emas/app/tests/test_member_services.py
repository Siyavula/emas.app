from datetime import datetime

import unittest2 as unittest
import transaction

from z3c.relationfield.relation import create_relation
from zope.component import createObject
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from emas.app.memberservice import MemberServicesDataAccess
from emas.app.memberservice import IMemberService
from emas.app.memberservice import MemberService
from emas.app.memberservice import SESSION

from emas.app.tests.base import INTEGRATION_TESTING


class TestMemberServiceIntegration(unittest.TestCase):
    """Unit test for the MemberService type
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.services = self.portal._getOb('products_and_services')
        self.intids = queryUtility(IIntIds, context=self.portal)
        self.dao = MemberServicesDataAccess(self.portal)
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def tearDown(self):
        session = SESSION()
        count = session.query(MemberService).filter(
            MemberService.memberid == TEST_USER_ID
        ).delete()
        print 'Deleted %s' % count
        transaction.commit()
    
    def test_get_all_memberservices(self):
        session = SESSION()
        db_ms = session.query(MemberService).all()
        all_ms = self.dao.get_all_memberservices()
        self.assertEquals(len(db_ms), len(all_ms))
        self.assertEquals(all_ms, db_ms)

    def test_get_memberservices(self):
        service = self.services.objectValues()[0]
        ms_args = self.get_ms_args(service, TEST_USER_ID)
        ms1_id= self.dao.add_memberservice(**ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        service_uids = [self.intids.getId(service),]
        memberid = TEST_USER_ID
        memberservices = \
            self.dao.get_memberservices(service_uids, memberid)
        self.assertEquals(memberservices, [ms1_db])

    def test_get_memberservices_by_subject(self):
        maths_services = \
            [s for s in self.services.objectValues() if s.subject == 'maths']
        for count in range(0,3):
            service = maths_services[count]
            ms_args = self.get_ms_args(service, TEST_USER_ID)
            self.dao.add_memberservice(**ms_args)

        science_services = \
            [s for s in self.services.objectValues() if s.subject == 'science']
        for count in range(0,3):
            service = science_services[count]
            ms_args = self.get_ms_args(service, TEST_USER_ID)
            self.dao.add_memberservice(**ms_args)

        memberservices = \
            self.dao.get_memberservices_by_subject(TEST_USER_ID, 'maths')
        self.assertEqual(len(memberservices), 3)
        memberservices = \
            self.dao.get_memberservices_by_subject(TEST_USER_ID, 'science')
        self.assertEqual(len(memberservices), 3)

    def test_get_memberservices_by_grade(self):
        grade_10_services = \
            [s for s in self.services.objectValues() if s.grade == 'grade-10']
        for count in range(0,3):
            service = grade_10_services[count]
            ms_args = self.get_ms_args(service, TEST_USER_ID)
            self.dao.add_memberservice(**ms_args)

        memberservices = \
            self.dao.get_memberservices_by_grade(TEST_USER_ID, 'grade-10')
        self.assertEqual(len(memberservices), 3)

    def test_get_memberservices_by_subject_and_grade(self):
        grade_10_maths_services = \
            [s for s in self.services.objectValues() if s.grade == 'grade-10']
        grade_10_maths_services = \
            [s for s in grade_10_maths_services if s.subject == 'maths']
        for count in range(0,3):
            service = grade_10_maths_services[count]
            ms_args = self.get_ms_args(service, TEST_USER_ID)
            self.dao.add_memberservice(**ms_args)

        memberservices = \
            self.dao.get_memberservices_by_subject_and_grade(TEST_USER_ID,
                                                             'maths',
                                                             'grade-10')
        self.assertEqual(len(memberservices), 3)

        memberservices = \
            self.dao.get_memberservices_by_subject_and_grade(TEST_USER_ID,
                                                             'science',
                                                             'grade-10')
        self.assertEqual(len(memberservices), 0)

    def test_get_active_memberservices(self):
        pass

    def test_get_active_memberservices_by_subject(self):
        pass

    def test_get_active_memberservices_by_grade(self):
        pass

    def test_get_active_memberservices_by_subject_and_grade(self):
        pass

    def test_get_expired_memberservices(self):
        pass

    def test_get_expired_memberservices_by_subject(self):
        pass

    def test_get_expired_memberservices_by_grade(self):
        pass

    def test_get_expired_memberservices_by_subject_and_grade(self):
        pass

    def test_get_memberservice_by_primary_key(self):
        pass

    def test_add_memberservice(self):
        service = self.services.objectValues()[0]
        ms_args = self.get_ms_args(service, TEST_USER_ID)
        ms1_id= self.dao.add_memberservice(**ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        self.failUnless(IMemberService.providedBy(ms1_db))

    def test_adding_duplicate_memberservices(self):
        service = self.services.objectValues()[0]
        ms_args = self.get_ms_args(service, TEST_USER_ID)
        ms1_id= self.dao.add_memberservice(**ms_args) 
        ms2_id= self.dao.add_memberservice(**ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        ms2_db = self.get_memberservice(ms2_id)
        self.failUnless(IMemberService.providedBy(ms1_db))

    def test_update_memberservice(self):
        service = self.services.objectValues()[0]
        ms_args = self.get_ms_args(service, TEST_USER_ID)
        ms1_id= self.dao.add_memberservice(**ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        ms1_db.title = 'new title'
        self.dao.update_memberservice(ms1_db)
        ms1_db = self.get_memberservice(ms1_id)
        self.assertEquals(ms1_db.title, 'new title')

    def test_delete_memberservice(self):
        service = self.services.objectValues()[0]
        ms_args = self.get_ms_args(service, TEST_USER_ID)
        ms1_id= self.dao.add_memberservice(**ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        self.dao.delete_memberservice(ms1_db)
        ms1_db = self.get_memberservice(ms1_id)
        self.assertEquals(ms1_db, None)

    def test_related_service(self):
        pass

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
    
    def get_memberservice(self, memberservice_id):
        session = SESSION()
        memberservices = session.query(MemberService).filter_by(
            id = memberservice_id).all()
        return memberservices and memberservices[0] or None

    def create_services(self):
        subjects = ['maths', 'science']
        grades = ['10', '11', '12']
        for subject in subjects:
            for count, grade in grades:
                props = {'service_type' : 'subscription',
                         'grade'        : grade,
                         'subject'      : subject,
                         'price'        : '111'}
                s_id = self.services.invokeFactory('emas.app.service',
                                                 '%s-%s' % (subject, grade),
                                                 **props)
                service = self.services._getOb(s_id)
                service.subject = props['subject']

    def get_ms_args(self, service, memberid):
        ms_args = {
            'memberid': memberid,
            'title': '%s for %s' % (service.title, memberid),
            'related_service_id': self.intids.getId(service),
            'expiry_date': datetime.now(),
        }
        return ms_args


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
