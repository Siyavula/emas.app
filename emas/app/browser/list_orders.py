from five import grok
from Acquisition import aq_inner

from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.tableview import Table as PloneTable
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from emas.app.order_folder import IOrderFolder
from emas.app.order import vocab_payment_methods
from emas.app import MessageFactory as _

grok.templatedir('templates')


class FieldIndexClause(object):
    def get(self, criterion, request):
        value = request.get(criterion)
        if not value:
            return None
        return {criterion: value}

class KeywordIndexClause(object):
    def get(self, criterion, request):
        values = request.get(criterion)
        if not values:
            return None
        return {criterion: [values]}

class StartDateIndexClause(object):
    def get(self, criterion, request):
        value = request.get(criterion)
        if not value:
            return None
        return {'ordered_date': {'min': date}}

class EndDateIndexClause(object):
    def get(self, criterion, request):
        value = request.get(criterion)
        if not value:
            return None
        return {'ordered_date': {'max': date}}

class DateRangeClause(object):
    def get(self, criterion, request):
        ordered_date = request.get('ordered_date', None)
        if not ordered_date:
            return None
        max_date = ordered_date.end
        min_date = ordered_date.start
        if max_date and min_date:
            return {'order_date': {'minmax': [min_date, max_date]}}
        else:
            return None


FIELDINDEX_CLAUSE = FieldIndexClause() 
KEYWORD_CLAUSE = KeywordIndexClause()
START_DATE_INDEX_CLAUSE = StartDateIndexClause()
END_DATE_INDEX_CLAUSE = EndDateIndexClause()
DATERANGE_CLAUSE = DateRangeClause()
FILTERS = {'review_state'        : FIELDINDEX_CLAUSE,
           'payment_method'      : FIELDINDEX_CLAUSE,
           'userid'              : FIELDINDEX_CLAUSE,
           'related_item_uuids'  : KEYWORD_CLAUSE,
           'getId'               : FIELDINDEX_CLAUSE,
           'id'                  : FIELDINDEX_CLAUSE,
           'order_date'          : DATERANGE_CLAUSE,
           'order_number'        : FIELDINDEX_CLAUSE,
           'verification_code'   : FIELDINDEX_CLAUSE,}

class List_Orders(grok.View, FolderContentsView):
    """
    """
    grok.context(IOrderFolder)
    grok.require('zope2.View')

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
            for criterion, clause_generator in FILTERS.items():
                clause = clause_generator.get(criterion, self.request)
                if clause:
                    query.update(clause)
                    got_filter_criteria = True
            
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
        return 'paid'

    def get_related_services_for(self, order):
        services = []
        for item in order.order_items():
            service = item.related_item.to_object
            services.append(service.Title())
        return services
