from datetime import datetime, timedelta

import unittest2 as unittest
import transaction

from z3c.relationfield.relation import create_relation
from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer

from emas.app import eventhandlers
from emas.app.tests.base import INTEGRATION_TESTING


class FauxEvent(object):
    action = 'pay'


class TestEventhandlers(unittest.TestCase):
    """ Unit test for the eventhandlers.
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.services = self.portal._getOb('products_and_services')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.orders = self.portal._getOb('orders')
        self.ordernumbers = []

    def tearDown(self):
        self.orders.manage_delObjects(self.ordernumbers)

    def test_eventhandler(self):
        service1 = self.services['science-grade12-monthly-practice']
        service1.access_group = ''
        ordernumber = '%04d' % 1
        self.ordernumbers.append(ordernumber)
        order1 = self.add_order(ordernumber, TEST_USER_ID, service1)

        event1 = FauxEvent()
        eventhandlers.onOrderPaid(order1, event1)

        service2 = self.services['science-grade12-practice']
        service2.access_group = ''
        ordernumber = '%04d' % 2
        self.ordernumbers.append(ordernumber)
        order2 = self.add_order(ordernumber, TEST_USER_ID, service2)

        event2 = FauxEvent()
        eventhandlers.onOrderPaid(order2, event2)
    
    def add_order(self, ordernumber, memberid, service):
        props = {'id'     :ordernumber,
                 'title'  :ordernumber,
                 'userid' :memberid}
        createContentInContainer(
            self.orders,
            'emas.app.order',
            False,
            **props
        )
        order = self.orders._getOb(ordernumber)

        order.fullname = 'test user'
        order.phone = '999999999999'
        order.shipping_address = ''
        order.payment_method = 'eft'

        item_id = 'orderitem.%s' %service.getId()
        relation = create_relation(service.getPhysicalPath())
        props = {'id'           :item_id,
                 'title'        :service.Title(),
                 'related_item' :relation,
                 'quantity'     :1}
        createContentInContainer(
            order,
            'emas.app.orderitem',
            False,
            **props
        )
        return order


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
