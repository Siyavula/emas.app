import hashlib

from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from plone.indexer import indexer

from emas.theme.interfaces import IEmasSettings

from emas.app.browser.utils import compute_vcs_response_hash
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


@indexer(IOrder)
def statehash(obj):
    return obj.__hash__()
grok.global_adapter(statehash, name="statehash")


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
        return self.objectValues()
    
    def may_transition_to_paid(self, **kwargs):
        """ We try to get the 'Hash' key from the request. It will be
            supplied by VCS on the return call. This is compared to the hash
            we compute from the data returned.

            This is done in order to stop the spoofing of successful payment
            responses.
        """
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IEmasSettings)
        md5key = settings.vcs_md5_key
        our_hash = compute_vcs_response_hash(self.REQUEST.form, md5key)
        vcs_returned_hash = self.REQUEST.get('Hash', '')
        return our_hash == vcs_returned_hash
    
    def __hash__(self):
        state = self._get_state_string()
        h = hashlib.new('ripemd160')
        h.update(state)
        return h.hexdigest()

    def __eq__(self, other):
        return self._get_state_tuple() == other._get_state_tuple()
    
    def __neq__(self, other):
        return self._get_state_tuple() != other._get_state_tuple()

    def __lt__(self, other):
        return self._get_state_tuple() < other._get_state_tuple()

    def __le__(self, other):
        return self._get_state_tuple() <= other._get_state_tuple()

    def __gt__(self, other):
        return self._get_state_tuple() > other._get_state_tuple()

    def __ge__(self, other):
        return self._get_state_tuple() >= other._get_state_tuple()

    def __cmp__(self, other):
        return self.__eq__(other)

    def _get_state_tuple(self):
        """ Returns the current state of this object as a tuple.
            *WARNING*
            This does not take any schemaextender or dexterity behaviour fields
            into account.
            *WARNING*
        """
        order_items = ''.join(
            [item._get_state_string() for item in self.order_items()])

        return (self.shipping_address,
                self.shipping_method,
                self.userid,
                self.fullname,
                self.phone,
                self.addvat,
                order_items)

    def _get_state_string(self):
        return '|'.join([str(e) for e in self._get_state_tuple()])
    

class SampleView(grok.View):
    grok.context(IOrder)
    grok.require('zope2.View')
    
    # grok.name('view')
