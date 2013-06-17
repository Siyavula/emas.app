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
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        if 'testfolder' not in self.portal.objectIds():
            self.portal.invokeFactory('Folder', 'testfolder')
        self.folder = self.portal.testfolder
        self.grade = '12'
        self.subject = 'maths'
        s_id = 'service1'
        if s_id not in self.folder.objectIds():
            self.folder.invokeFactory('emas.app.service',
                                      s_id,
                                      service_type='subscription',
                                      grade=self.grade,
                                      subject=self.subject,
                                      price='111')
        self.service = self.folder._getOb(s_id)
        self.intids = queryUtility(IIntIds, context=self.portal)
        self.ms_args = {
            'memberid': TEST_USER_ID,
            'title': '%s for %s' % (self.service.title, TEST_USER_ID),
            'related_service_id': self.intids.getId(self.service),
            'expiry_date': datetime.now(),
        }
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
        ms1_id= self.dao.add_memberservice(**self.ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        service_uids = [self.intids.getId(self.service),]
        memberid = TEST_USER_ID
        memberservices = \
            self.dao.get_memberservices(service_uids, memberid)
        self.assertEquals(memberservices, [ms1_db])

    def test_get_memberservices_by_subject(self):
        pass

    def test_get_memberservices_by_grade(self):
        pass

    def test_get_memberservices_by_subject_and_grade(self):
        pass

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
        ms1_id= self.dao.add_memberservice(**self.ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        self.failUnless(IMemberService.providedBy(ms1_db))

    def test_adding_duplicate_memberservices(self):
        ms1_id= self.dao.add_memberservice(**self.ms_args) 
        ms2_id= self.dao.add_memberservice(**self.ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        ms2_db = self.get_memberservice(ms2_id)
        self.failUnless(IMemberService.providedBy(ms1_db))

    def test_update_memberservice(self):
        ms1_id= self.dao.add_memberservice(**self.ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        ms1_db.title = 'new title'
        self.dao.update_memberservice(ms1_db)
        ms1_db = self.get_memberservice(ms1_id)
        self.assertEquals(ms1_db.title, 'new title')

    def test_delete_memberservice(self):
        ms1_id= self.dao.add_memberservice(**self.ms_args) 
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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
