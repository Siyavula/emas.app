from DateTime import DateTime
from Products.PlonePAS.tools.membership import MembershipTool
from AccessControl.SecurityManagement import getSecurityManager


def setLoginTimes(self):
    """ Changed into a no-op in order to stop ZODB access on each login.
        It is unnecessary and kills the app's performance.
    """ 
    initialLogin = False
    member = getSecurityManager().getUser()
    if member is not None:
        default = DateTime('2000/01/01')
        login_time = member.getProperty('login_time', default)
        if login_time == default:
            initialLogin = True
	    login_time = DateTime()
            member.setProperties(login_time=self.ZopeTime(),
                                 last_login_time=login_time)
    return initialLogin

MembershipTool.setLoginTimes = setLoginTimes
