from five import grok
from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

from emas.theme.interfaces import IEmasServiceCost

grok.templatedir('templates')

class Order(grok.View):
    """ Order form.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    def __call__(self):
        self.grade = None
        self.prod_practice_book = None
        self.subjects = None
        if self.request.has_key('order.form.submitted'):
            # validate form
            self.grade = self.request.form.get('grade', None)
            self.prod_practice_book = self.request.form.get('prod_practice_book', None)
            self.subjects = self.request.form.get('subjects', None)
            names = ['selected_subjects', 'selected_grade', 'selected_product']
            self.missing_fields = \
                [name for name in names if getattr(self, name, None) is None]
        
            if self.grade and self.prod_practice_book and self.subjects:
                # traverse to confirm if form has required fields
                view = self.context.restrictedTraverse('@@confirm')
                return view()
                
        return super(Order, self).__call__()

    def update(self):
        if self.request.has_key('order.form.submitted'):
            pmt = getToolByName(self.context, 'portal_membership')
            if pmt.isAnonymousUser():
                self.context.restrictedTraverse('logged_in')()

            if not(self.grade and self.prod_practice_book and self.subjects):
                pps = self.context.restrictedTraverse('@@plone_portal_state')
                ptool = pps.portal().plone_utils
                ptool.addPortalMessage('All fields are required.', 'warning')

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IEmasServiceCost)
        self.practiceprice = settings.practiceprice
        self.textbookprice = settings.textbookprice
        self.textbook_and_practiceprice = (
            self.practiceprice + self.textbookprice)

    def products_and_services(self):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        products_and_services = pps.portal()._getOb('products_and_services')
        return products_and_services.getFolderContents(full_objects=True)

    def action(self, isAnon):
        """ Post to the current view in order to validate the form.
            We need enough info on the form for the confirm view to work.
        """
        return '%s/@@order' %self.context.absolute_url()
        
    def subjects(self):
        return self.request.get('subjects', '')
   
    def subject_selected(self, subject, selected):
        return subject == selected and 'checked' or ''

    def grade(self):
        return self.request.get('grade', '')

    def grade_selected(self, grade, selected):
        return grade == selected and 'checked' or ''

    def prod_practice_book(self):
        return self.request.get('prod_practice_book', '')

    def prod_practice_book_selected(self, prod_practice_book, selected):
        return prod_practice_book == selected and 'checked' or ''

    def prod_payment(self):
        return self.request.get('prod_payment', '')

    def prod_payment_selected(self, prod_payment, selected):
        return prod_payment == selected and 'checked' or ''

    def fullname(self):
        return self.request.get('fullname', '')

    def phone(self):
        return self.request.get('phone', '')

    def shipping_address(self):
        return self.request.get('shipping_address', '')

    def ordernumber(self):
        return self.request.get('ordernumber', '')

