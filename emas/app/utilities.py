import random
from types import IntType
from persistent import Persistent
from BTrees.IIBTree import IIBTree
from zope.interface import implements, Interface

RETRIES = 1000
LOWER = 9999
UPPER = 100000


class IVerificationCodeUtility(Interface):
    
    def generate(self, order):
        """
        """

    def is_unique(self, context, verification_code):
        """
        """

    def add(self, verification_code, order):
        """
        """


class VerificationCodeUtility(Persistent):
    
    implements(IVerificationCodeUtility)

    def __init__(self):
        self._verification_codes = IIBTree()

    def generate(self, order):
        verification_code = random.randint(LOWER, UPPER)
        count = 0
        while not self.is_unique(verification_code) and count < RETRIES:
            count += 1
            verification_code = random.randint(LOWER, UPPER)

        if count > RETRIES - 1:
            raise Exception('Could not find unique verification code.')
        
        self.add(verification_code, order)
        return str(verification_code)
        
    def is_unique(self, code):
        if code in self._verification_codes.keys():
            return False
        else:
            return True

    def add(self, verification_code, order):
        order_id = order.getId()
        if not isinstance(order_id, IntType):
            order_id = int(order_id)

        self._verification_codes[verification_code] = order_id
