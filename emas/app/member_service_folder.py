from five import grok
from plone.directives import dexterity, form

from zope import schema

from emas.app import MessageFactory as _


class IMemberServiceFolder(form.Schema):
    """
    Container for member services.
    """

class MemberServiceFolder(dexterity.Container):
    grok.implements(IMemberServiceFolder)
    

class SampleView(grok.View):
    grok.context(IMemberServiceFolder)
    grok.require('zope2.View')
    
    # grok.name('view')
