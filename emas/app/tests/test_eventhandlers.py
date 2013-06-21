from datetime import datetime, timedelta

import unittest2 as unittest
import transaction

from z3c.relationfield.relation import create_relation
from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from emas.app.tests.base import INTEGRATION_TESTING


class TestEventhandlers(unittest.TestCase):
    """ Unit test for the eventhandlers.
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.services = self.portal._getOb('products_and_services')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def test_eventhandler(self):
        self.fail()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
