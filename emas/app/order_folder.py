from five import grok
from plone.directives import dexterity, form

from zope import schema

from emas.app import MessageFactory as _


class IOrderFolder(form.Schema):
    """
    Container for member orders.
    """


class OrderFolder(dexterity.Container):
    grok.implements(IOrderFolder)
    

class SampleView(grok.View):
    grok.context(IOrderFolder)
    grok.require('zope2.View')
    
    # grok.name('view')
