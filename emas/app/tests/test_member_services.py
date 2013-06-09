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

from emas.app.browser import utils
from emas.app.alchemy.memberservice import IMemberService
from emas.app.alchemy.memberservice import MemberService
from emas.app.alchemy import SESSION

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
        self.intids = queryUtility(IIntIds, context=self.portal)
        self.ms_args = {
            'memberid': TEST_USER_ID,
            'title': '%s for %s' % (self.service.title, TEST_USER_ID),
            'related_service_id': self.intids.getId(self.service),
            'expiry_date': datetime.now(),
        }
    
    def test_adding(self):
        ms1_id= utils.add_memberservice(**self.ms_args) 
        ms1_db = self.get_memberservice(ms1_id)
        self.failUnless(IMemberService.providedBy(ms1))

    def test_adding_duplicates(self):
        ms1= utils.add_memberservice(**self.ms_args) 
        ms2= utils.add_memberservice(**self.ms_args) 
        self.failUnless(IMemberService.providedBy(ms1))

    def test_updating(self):
        ms1_id= utils.add_memberservice(**self.ms_args) 
        ms1 = self.get_memberservice(ms1_id)
        ms1.title = 'new title'
        utils.update_memberservice(ms1)
        ms1 = self.get_memberservice(ms1_id)
        self.assertEquals(ms1.title, 'new title')

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
        return memberservices[0]


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
