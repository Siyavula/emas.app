import datetime
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
    grok.require('zope2.View')

    title = 'Orders'

    def update(self):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        self.portal = pps.portal()
        self.orders_folder = self.portal.orders
        self.orders = []

        if self.request.has_key('list_orders.form.submitted'):
            # we have to have *some* filter criteria or the search will take
            # forever.
            got_filter_criteria = False
            oc = getToolByName(self.context, 'order_catalog')

            query = {'portal_type': 'emas.app.order',
                     'path': '/'.join(self.orders_folder.getPhysicalPath())}
            
            # make it a dict, because I want an easy way to get rid of some keys
            filter_criteria = DictType(self.request['filter_criteria'])
            if filter_criteria:
                got_filter_criteria = True

            now = datetime.datetime.now()
            yesterday = now - datetime.timedelta(1)
            tomorrow = now + datetime.timedelta(1)

            start_date = filter_criteria.get('order_date_start', yesterday)
            filter_criteria.pop('order_date_start', None)
            end_date = filter_criteria.get('order_date_end', tomorrow)
            filter_criteria.pop('order_date_end', None)
            query['start_date'] = {'minmax': [start_date, end_date]}
            
            for key, value in filter_criteria.items():
                query[key] = value
            
            if got_filter_criteria:
                self.orders = oc(query)
                if not self.orders:
                    self.context.plone_utils.addPortalMessage(
                        _('No orders match your search criteria.')
                    )
            else:
                self.context.plone_utils.addPortalMessage(
                    _('Please supply search criteria.')
                )
        b_size = int(self.request.get('b_size', 50))
        b_start = int(self.request.get('b_start', 0))
        self.orders = Batch(self.orders, b_size, b_start)
            
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
