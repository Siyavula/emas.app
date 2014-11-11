import json
import urllib2
import logging
import transaction
from DateTime import DateTime
from Products.PlonePAS.tools.membership import MembershipTool
from Products.PlonePAS.tools.memberdata import MemberData
from AccessControl.SecurityManagement import getSecurityManager

LOG = logging.getLogger('emas.app.patches')

class PutRequest(urllib2.Request):
    def get_method(self):
        return 'PUT'

class SyncProfileTask(object):
    def __init__(self, uuid):
        self.uuid = uuid
        self.mapping = {}
        tx = transaction.get().addAfterCommitHook(self)

    def addChanges(self, m):
        self.mapping.update(m)

    def __call__(self, status):
        if status:
            req = PutRequest('http://localhost:6543/profile/update/{0}'.format(self.uuid))
            req.add_header('Content-Type', 'application/json')
            try:
                urllib2.urlopen(req, json.dumps({'emas': self.mapping}))
            except urllib2.HTTPError, e:
                try:
                    edoc = json.loads(e.read())
                    LOG.error(edoc['error']['message'])
                except:
                    pass
                raise e

def setLoginTimes(self):
    """ Changed into a no-op in order to stop ZODB access on each login.
        It is unnecessary and kills the app's performance.
    """ 
    res = False
    if not self.isAnonymousUser():
        member = self.getAuthenticatedMember()
        default = DateTime('2000/01/01')
        login_time = member.getProperty('login_time', default)
        if login_time == default:
            res = True
            login_time = DateTime()
            member.setProperties(login_time=self.ZopeTime(),
                                 last_login_time=login_time)
    return res

def setPassword(self, password, domains=None, REQUEST=None):
    if not self.isAnonymousUser():
        uuid = self.getAuthenticatedMember().getProperty('profile_uuid', None)
        if uuid is not None:
            req = PutRequest('http://localhost:6544/users/{0}'.format(uuid))
            req.add_header('Content-Type', 'application/json')
            try:
                urllib2.urlopen(req, json.dumps({
                    'password': password
                }))
            except urllib2.HTTPError, e:
                try:
                    edoc = json.loads(e.read())
                    LOG.error(edoc['error']['message'])
                except:
                    pass

                raise e

    return self._emas_setPassword(password, domains, REQUEST)

MembershipTool.setLoginTimes = setLoginTimes
MembershipTool._emas_setPassword = MembershipTool.setPassword
MembershipTool.setPassword = setPassword


def setMemberProperties(self, mapping, force_local=0):
    request = self.REQUEST
    uuid = self.getProperty('profile_uuid', None)
    if uuid is not None:
        # One task syncer per request
        if '__syncprofile' not in request:
            request['__syncprofile'] = SyncProfileTask(uuid)
        synctask = request['__syncprofile']

        for k, v in mapping.items():
            changes = {}
            if k == 'fullname':
                if v.strip() != '':
                    entries = v.strip().split()
                    changes['name'] = ' '.join(entries[:-1])
                    if len(entries) > 1:
                        changes['surname'] = entries[-1]
            elif k in ('email', 'userrole', 'school', 'province',
                    'subscribe_to_newsletter', 'registrationdate'):
                changes[k] = v
        # update on profile server.
        synctask.addChanges(changes)

    return self._emas_setMemberProperties(mapping, force_local)

MemberData._emas_setMemberProperties = MemberData.setMemberProperties
MemberData.setMemberProperties = setMemberProperties
