from datetime import datetime
from persistent import Persistent
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implements
from zope.intid import IIntIds
from zope.index.text.textindex import TextIndex
from zope.index.field import FieldIndex

from Products.CMFCore.utils import getToolByName
from BTrees.IOBTree import IOBTree

class IUserCatalog(Interface):
    """ Index and search on user's login, full name and email 
    """

class UserCatalog(Persistent):

    implements(IUserCatalog)

    def __init__(self):
        self._index = TextIndex()
        self._regdate = FieldIndex()
        self._metadata = IOBTree()

    def index(self, user):
        ints = getUtility(IIntIds)  
        site = getSite()
        mtool = getToolByName(site, 'portal_membership')
        memberdata = mtool.getMemberById(user.getId())
        if memberdata is None:
            return
        memberid = ints.register(memberdata)
        text = "%s %s %s" % (memberdata.getUserName(),
                             memberdata.getProperty('fullname'),
                             memberdata.getProperty('email'))
        regdate = memberdata.getProperty('registrationdate')
        regdate = datetime.strptime(regdate.strftime("%Y-%m-%d"), "%Y-%m-%d")
        self._index.index_doc(memberid, text)
        self._regdate.index_doc(memberid, regdate)
        self._metadata[memberid] = {
            'username': memberdata.getUserName(),
            'fullname': memberdata.getProperty('fullname'),
            'email': memberdata.getProperty('email'),
            'registrationdate': memberdata.getProperty('registrationdate')
            }

    def unindex(self, member):
        ints = getUtility(IIntIds)  
        memberid = ints.register(member)
        self._index.unindex_doc(memberid)
        self._regdate.unindex_doc(memberid)

    def search(self, searchstring='', regdate=None):
        ints = getUtility(IIntIds)  
        site = getSite()
        mtool = getToolByName(site, 'portal_membership')
        if searchstring:
            res = self._index.apply(searchstring).keys()
        else:
            res = []
        if regdate:
            res2 = self._regdate.apply(regdate)
            # get the intersection between the two results
            memberids = []
            if searchstring:
                for e in res:
                    if e in res2:
                        memberids.append(e)
            memberids = res2
        else:
            memberids = res
        result = []
        for k in memberids:
            result.append(self._metadata[k])
        return result

