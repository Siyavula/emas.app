import datetime
from DateTime import DateTime as DT
from types import DictType

from five import grok
from Acquisition import aq_inner

from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.tableview import Table as PloneTable
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch

from emas.app.order_folder import IOrderFolder
from emas.app.order import vocab_payment_methods
from emas.app import MessageFactory as _

grok.templatedir('templates')


class List_Orders(grok.View):
    """
    """
    grok.context(IOrderFolder)
    grok.require('zope2.ManageProperties')

    title = 'Orders'

    def update(self):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        self.portal = pps.portal()
        self.orders_folder = self.portal.orders
        self.orders = []

        if self.request.has_key('list_orders.form.submitted'):
            # we have to have *some* filter criteria or the search will take
            # forever.
            oc = getToolByName(self.context, 'order_catalog')

            query = {'portal_type': 'emas.app.order',
                     'path': '/'.join(self.orders_folder.getPhysicalPath())}
            
            # make it a dict, because I want an easy way to get rid of some keys
            filter_criteria = DictType(self.request.get('filter_criteria', {}))

            now = DT()
            yesterday = now - 1
            tomorrow = now + 1

            start_date = self.request['order_date_start']
            end_date = self.request['order_date_end']
            if start_date and end_date:
                start_date = DT(self.request['order_date_start'])
                end_date = DT(self.request['order_date_end'])
                date_query = {'query': [start_date, end_date], 'range': 'minmax'}
                query['order_date'] = date_query
            
            for key, value in filter_criteria.items():
                query[key] = value
            
	    self.orders = oc(query)
	    if self.orders:
                b_size = int(self.request.get('b_size', 50))
                b_start = int(self.request.get('b_start', 0))
                self.orders = Batch(self.orders, b_size, b_start)
            else:
	        self.context.plone_utils.addPortalMessage(
	    	_('No orders match your search criteria.')
	        )
            
    def review_states(self):
        return [['ordered', 'Ordered'],
                ['paid'   , 'Paid'],]

    def payment_methods(self):
        return vocab_payment_methods
    
    def services(self):
        services = []
        for item in self.portal.products_and_services.objectValues():
            uuid = IUUID(item)
            services.append([uuid, item.Title()])
        return services
    
    def get_review_state_for(self, order):
        wft = getToolByName(self.context, 'portal_workflow')
        status = wft.getStatusOf('order_workflow', order) 
        return status['review_state']

    def get_related_services_for(self, order):
        services = []
        for item in order.order_items():
            service = item.related_item.to_object
            services.append(service.Title())
        return services
