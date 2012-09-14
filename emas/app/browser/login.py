from zope.component import queryUtility, queryAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from emas.app import MessageFactory as _


class LoginFromOrderForm(BrowserView):
    """ We need our own login form in order to set the required values on the
        request. This enables the order view to call logged_in and trigger
        the user.
    """
    
    def __call__(self):
        return self.index()
