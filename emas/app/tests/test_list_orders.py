from datetime import datetime, timedelta

import unittest2 as unittest
import transaction

from AccessControl import Unauthorized
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


class TestListOrders(unittest.TestCase):
    """Unit test for the list_orders view
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        return
    
    def test_view_unauthorized(self):
        """ This view should only be accessible to members with the 'Manageer'
            role.
        """
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        try:
            self.portal.orders.restrictedTraverse('@@list_orders')
        except Unauthorized:
            return
        else:
            self.fail()

    def test_view_authorized(self):
        """ This view should only be accessible to members with the 'Manageer'
            role.
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.orders.restrictedTraverse('@@list_orders')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
