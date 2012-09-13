from five import grok
from Acquisition import aq_inner

from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.tableview import Table as PloneTable

from emas.app.order_folder import IOrderFolder

grok.templatedir('templates')

class List_Orders(grok.View, FolderContentsView):
    """
    """
    grok.context(IOrderFolder)
    grok.require('zope2.View')
    
    def contents_table(self):
        table = ContentsTable(aq_inner(self.context), self.request)
        return table.render()
    

class ContentsTable(FolderContentsTable):
    """
    The contents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter=None):
        super(ContentsTable, self).__init__(context, request, contentFilter)
        url = context.absolute_url()
        view_url = url + '/@@list_orders'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)


class Table(PloneTable):
    """ Custom table renderer for contents
    """                

    render = ViewPageTemplateFile("./templates/table.pt")

