import random
from persistent import Persistent
from BTrees.OOBTree import OOBTree
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
        self._verification_codes = OOBTree()

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
        return self._verification_codes.has_key(code) and False or True

    def add(self, verification_code, order):
        self._verification_codes[verification_code] = order
    
    def _p_resolveConflict(self, old, vc1, vc2):
        import pdb;pdb.set_trace()
        raise 'Not implemented yet.'
        return self.generate_verification_code 
