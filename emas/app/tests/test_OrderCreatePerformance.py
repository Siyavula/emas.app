# -*- coding: iso-8859-15 -*-
"""order_create_performance FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data
#from funkload.utils import xmlrpc_get_credential

class OrderCreatePerformance(FunkLoadTestCase):
    """XXX

    This test use a configuration file OrderCreatePerformance.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp")
        self.server_url = self.conf_get('main', 'url')
        # XXX here you can setup the credential access like this
        # credential_host = self.conf_get('credential', 'host')
        # credential_port = self.conf_getInt('credential', 'port')
        # self.login, self.password = xmlrpc_get_credential(credential_host,
        #                                                   credential_port,
        # XXX replace with a valid group
        #                                                   'members')

    def test_order_create_performance(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------

        # /tmp/tmpv3cBhX_funkload/watch0091.request
        self.get(server_url + "/emas/login?ajax_load=1353851071541",
            description="Get /emas/login")
        # /tmp/tmpv3cBhX_funkload/watch0092.request
        self.post(server_url + "/emas/login_form", params=[
            ['came_from', 'http://emas:8080/emas'],
            ['next', ''],
            ['ajax_load', '1353851071541'],
            ['ajax_include_head', ''],
            ['target', ''],
            ['mail_password_url', ''],
            ['join_url', ''],
            ['form.submitted', '1'],
            ['js_enabled', '0'],
            ['cookies_enabled', ''],
            ['login_name', ''],
            ['pwd_empty', '0'],
            ['__ac_name', 'tester080'],
            ['__ac_password', '12345'],
            ['submit', 'Log in']],
            description="Post /emas/login_form")
        # /tmp/tmpv3cBhX_funkload/watch0094.request
        self.get(server_url + "/emas",
            description="Get /emas")
        # /tmp/tmpv3cBhX_funkload/watch0129.request
        self.get(server_url + "/emas/order",
            description="Get /emas/order")
        # /tmp/tmpv3cBhX_funkload/watch0164.request
        self.post(server_url + "/emas/@@confirm", params=[
            ['order.form.submitted', 'true'],
            ['isAnon', 'False'],
            ['ordernumber', ''],
            ['subjects', 'Maths,Science'],
            ['grade', 'grade12'],
            ['prod_practice_book', 'Practice,Textbook'],
            ['prod_payment', 'eft'],
            ['fullname', ''],
            ['phone', ''],
            ['shipping_address', ''],
            ['submitorder', '1']],
            description="Post /emas/@@confirm")

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
