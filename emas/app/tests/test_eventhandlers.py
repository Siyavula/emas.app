import os

from base import BaseFunctionalTestCase

dirname = os.path.dirname(__file__)

class TestEventhandlers(BaseFunctionalTestCase):
    """ Test the intelligent practice messages service viewlets  """
    
    def setUp(self):
        super(TestEventhandlers, self).setUp()
    
    def test_eventhandlers(self):
        self.fail()
