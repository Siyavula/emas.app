from five import grok
from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasServiceCost

grok.templatedir('templates')

class Order(grok.View):
    """ Order form.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    
    def update(self):
        #TODO: check for authed before re-authing
        self.context.restrictedTraverse('logged_in')()

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
        """ We cannot go to the 'confirm' view until the user has
            authenticated, since the 'confirm' view has to create objects on
            behalf of the authenticated user. That is why we rather submit back
            to the 'order' view.
        """
        url = '%s/@@confirm' %self.context.absolute_url()
        if isAnon:
            url = '%s/@@order' %self.context.absolute_url()
        return url
        
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

