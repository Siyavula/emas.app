from five import grok
from Acquisition import aq_inner

from plone.directives import dexterity, form

from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.tableview import Table as PloneTable

from emas.app import MessageFactory as _


class IMemberServiceFolder(form.Schema):
    """
    Container for member services.
    """

class MemberServiceFolder(dexterity.Container):
    grok.implements(IMemberServiceFolder)
    

class Manage_MemberServices(grok.View, FolderContentsView):
    grok.context(IMemberServiceFolder)
    grok.require('zope2.View')
    grok.name('manage-memberservices')

    def contents_table(self):
        cFilter = ''
        if self.request.form.get('find-member-services'):
            cFilter = {'userid': self.request.form.get('memberid')}
        table = ContentsTable(aq_inner(self.context), self.request, cFilter)
        return table.render()


class ContentsTable(FolderContentsTable):
    """
    The contents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter=None):
        super(ContentsTable, self).__init__(context, request, contentFilter)
        url = context.absolute_url()
        view_url = url + '/@@manage-memberservices'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)


class Table(PloneTable):
    """ Custom table renderer for contents
    """                
    render = ViewPageTemplateFile("./member_service_folder_templates/table.pt")
