from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from z3c.form import group, field
from z3c.relationfield.schema import RelationList, RelationChoice

from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText

from emas.app import MessageFactory as _


class IOrderItem(form.Schema):
    """
    An order line item.
    """
    related_item = RelationChoice(
        title=_(u'label_related_item', default=u'Related Item'),
        source=ObjPathSourceBinder(
          object_provides='emas.app.product.IProduct'),
        required=True,
    )

    quantity = schema.Int(
        title=_(u"Quantity"),
        description=_("The quantity."),
        required=True,
    )

    price = schema.Float(
        title=_(u"Price"),
        description=_(
            ("The price. If you don't set this the related item's "
             "price will be used.")
        ),
        required=False,
    )

    total = schema.Float(
        title=_(u"Total"),
        description=_("The total."),
        required=False,
    )


class OrderItem(dexterity.Item):
    grok.implements(IOrderItem)


class SampleView(grok.View):
    grok.context(IOrderItem)
    grok.require('zope2.View')
    
    # grok.name('view')
