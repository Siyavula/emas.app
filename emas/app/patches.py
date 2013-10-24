from Products.PlonePAS.tools.membership import MembershipTool


def setLoginTimes(self):
    """ Changed into a no-op in order to stop ZODB access on each login.
        It is unnecessary and kills the app's performance.
    """ 
    return False

MembershipTool.setLoginTimes = setLoginTimes
