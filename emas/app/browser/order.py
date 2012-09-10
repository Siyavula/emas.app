from five import grok
from zope.interface import Interface

from plone.registry.interfaces import IRegistry

from emas.theme.interfaces import IEmasSettings

grok.templatedir('templates')

class Order(grok.View):
    """ Order form.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

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
        return grade == grade and 'checked' or ''

    def prod_practice_book(self):
        return self.request.get('prod_practice_book', '')

    def prod_practice_book_selected(self, prod_practice_book, selected):
        return prod_practice_book == selected and 'checked' or ''

    def prod_payment(self):
        return self.request.get('prod_payment', '')

    def prod_payment_selected(self, prod_payment, selected):
        return prod_payment == selected and 'checked' or ''

