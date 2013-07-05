from five import grok
from Acquisition import aq_inner

from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.tableview import Table as PloneTable

from Products.CMFCore.utils import getToolByName

from emas.app.order_folder import IOrderFolder
from emas.app import MessageFactory as _

grok.templatedir('templates')


FILTERS = ['review_state',
           'payment_method',
           'userid',
           'related_item_uuids',
           'getId',
           'id',
           'order_date',
           'order_number',
           'verification_code',]

class List_Orders(grok.View, FolderContentsView):
    """
    """
    grok.context(IOrderFolder)
    grok.require('zope2.View')

    def update(self):
        self.orders = []

        if self.request.has_key('list_orders.form.submitted'):
            # we have to have *some* filter criteria or the search will take
            # forever.
            got_filter_criteria = False
            pps = self.context.restrictedTraverse('@@plone_portal_state')
            portal = pps.portal()
            self.orders_folder = portal.orders
            oc = getToolByName(self.context, 'order_catalog')

            query = {'portal_type': 'emas.app.order',
                     'path': '/'.join(self.orders_folder.getPhysicalPath())}
            for key in FILTERS:
                value = self.request.get(key, None)
                if value:
                    got_filter_criteria = True
                    query[key] = value
            
            if got_filter_criteria:
                self.orders = oc(query)
            else:
                self.context.plone_utils.addPortalMessage(
                    _('Please supply search criteria.')
                )
            
            if not self.orders:
                self.context.plone_utils.addPortalMessage(
                    _('No orders matching your search criteria.')
                )
