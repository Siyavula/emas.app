from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from emas.theme.interfaces import IEmasSettings

from emas.app.browser.paymentdetails import vcs_hash
from emas.app import MessageFactory as _


vocab_shipping_methods = SimpleVocabulary(
    [SimpleTerm(value=u'postal_service', title=_(u'Postal service')),
     SimpleTerm(value=u'courier', title=_(u'Courier')),
    ]
)

# TODO: make this a portal property
VAT = 0.14


class IOrder(form.Schema):
    """
    Container for orderable items like products and services
    """
    date_ordered = schema.Date(
        title=_(u"Date ordered"),
        required=False,
    )

    shipping_address = schema.Text(
        title=_(u"Shipping address"),
        required=False,
    )

    shipping_method = schema.Choice(
        title=_(u"Shipping method"),
        vocabulary=vocab_shipping_methods,
        required=False,
    )

    userid = schema.TextLine(
        title=_(u"User id"),
        required=False,
    )

    fullname = schema.TextLine(
        title=_(u"Full name"),
        required=False,
    )

    phone = schema.TextLine(
        title=_(u"Phone number"),
        required=False,
    )

    addvat = schema.Bool(
        title=_(u"Add VAT"),
        required=True,
        default=False,
    )


class Order(dexterity.Container):
    grok.implements(IOrder)
    
    def subtotal(self):
        subtotal = 0
        items = self.objectValues()
        for item in items:
            subtotal += item.price
        return subtotal
        
    def vat(self, subtotal):
        vat = 0
        if self.addvat:
            vat = subtotal * VAT
        return vat

    def total(self):
        subtotal = self.subtotal()
        vat = self.vat(subtotal)
        return subtotal + vat

    def order_items(self):
        return self.getFolderContents(full_objects=True)
    
    def may_transition_to_paid(self, **kwargs):
        """ This method expects a dictionary like object as part of the 
            keyword args. The 'wf.doActionFor' call from 
            emas.app.browser.vcsresponseprocessor currently supplies this and
            we access it as 'request' in this method.

            We try to get the 'Hash' key from this dictionary. It will be
            supplied by VCS on the return call. This is compared to the hash
            we stored in an annotation on the order object just before passing
            payment control to VCS.

            This is done in order to stop the spoofing of successful payment
            responses.
        """
        pps = self.restrictedTraverse('@@plone_portal_state')
        member = pps.member()
        pmt = getToolByName(self, 'portal_membership')
        manage_portal = pmt.checkPermission(ManagePortal, self)
        if manage_portal:
            return True
        
        stored_vcs_hash = get_annotation('vcs_hash')
        original_hash = request.get('Hash', '')
        return original_hash == stored_vcs_hash


class SampleView(grok.View):
    grok.context(IOrder)
    grok.require('zope2.View')
    
    # grok.name('view')
