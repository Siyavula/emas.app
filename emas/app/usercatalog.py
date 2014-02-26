from persistent import Persistent
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implements
from zope.intid import IIntIds
from zope.index.text.textindex import TextIndex

from Products.CMFCore.utils import getToolByName

class IUserCatalog(Interface):
    """ Index and search on user's login, full name and email 
    """

class UserCatalog(Persistent):

    implements(IUserCatalog)

    def __init__(self):
        self._index = TextIndex()

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
        self._index.index_doc(memberid, text)

    def unindex(self, member):
        ints = getUtility(IIntIds)  
        memberid = ints.register(member)
        self._index.unindex_doc(memberid)

    def search(self, searchstring):
        ints = getUtility(IIntIds)  
        site = getSite()
        mtool = getToolByName(site, 'portal_membership')
        result = []
        for k, v in self._index.apply(searchstring).items():
            member = ints.getObject(k)
            member = mtool.getMemberById(member.id)
            result.append(member)
        return result

