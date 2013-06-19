import urllib
from five import grok
from Acquisition import aq_inner

from zope.component import getMultiAdapter
from zope.interface import Interface

from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.tableview import Table as PloneTable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import pretty_title_or_id

from emas.app.browser.utils import practice_service_intids
from emas.app.browser.utils import service_url as get_service_url
from emas.app.memberservice import MemberServicesDataAccess


grok.templatedir('templates')

class MemberServices(grok.View):
    """ Returns all the authenticated member's services
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('member-services')

    def update(self):
        self.service_intids = practice_service_intids(self.context)
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        memberid = pps.member().getId()
        self.dao = MemberServicesDataAccess(self.context)
        self.memberservices = []
        self.memberservices = \
            self.dao.get_active_memberservices(memberid)

    def service_url(self, service):
        return ''


class ActiveMemberServicesFor(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('active-memberservices-for')

    def update(self):
        self.memberservices = []
        self.dao = MemberServicesDataAccess(self.context)
        self.userid = self.request.get('userid', '')
        if self.userid:
            ids = practice_service_intids(self.context)
            dao = MemberServicesDataAccess(self.context)
            self.memberservices = dao.get_active_memberservices(self.userid)


class ListMemberServices(grok.View, FolderContentsView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('list-memberservices')
    grok.template('list_memberservices')

    def contents_table(self):
        table = ContentsTable(aq_inner(self.context), self.request)
        return table.render()


class ContentsTable(FolderContentsTable):
    """
    The contents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter=None):
        self.dao = MemberServicesDataAccess(context)
        super(ContentsTable, self).__init__(context, request, contentFilter)
        url = context.absolute_url()
        view_url = url + '/@@list-memberservices'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    def contentsMethod(self):
        return self.dao.get_all_memberservices

    def folderitems(self):
        """
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        portal_properties = getToolByName(context, 'portal_properties')
        contentsMethod = self.contentsMethod()
        show_all = self.request.get('show_all', '').lower() == 'true'
        pagesize = 20
        pagenumber = int(self.request.get('pagenumber', 1))
        start = (pagenumber - 1) * pagesize
        end = start + pagesize

        results = []
        for i, obj in enumerate(contentsMethod()):
            db_primary_key = obj.id

            # avoid creating unnecessary info for items outside the current
            # batch;  only the db_primary_key is needed for the "select all" case...
            # Include brain to make customizations easier (see comment below)
            if not show_all and not start <= i < end:
                results.append(dict(db_primary_key=db_primary_key, brain=obj))
                continue

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = context.absolute_url()

            results.append(dict(
                memberservice = obj,
                url = url,
                id = obj.id,
                quoted_id = obj.id,
                db_primary_key = db_primary_key,
                view_url = '#',
                table_row_class = table_row_class,
            ))
        return results


class Table(PloneTable):
    """ Custom table renderer for memberservices 
    """                

    render = ViewPageTemplateFile("./templates/memberservices_table.pt")

