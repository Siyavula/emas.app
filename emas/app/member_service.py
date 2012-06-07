from datetime import datetime, date
import DateTime
from five import grok
from plone.directives import dexterity, form
from plone.indexer import indexer
from plone.uuid.interfaces import IUUID

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from emas.app import MessageFactory as _


NULLDATE = date(1970, 01, 01)

class IMemberService(form.Schema):
    """
    An object that describes the services or products a member bought.
    """

    userid = schema.TextLine(
        title=_(u"User id"),
        required=False,
    )

    related_service = RelationChoice(
        title=_(u'label_related_service', default=u'Related Service'),
        source=ObjPathSourceBinder(
          object_provides='emas.app.product.IProduct'),
        required=False,
    )

    expiry_date = schema.Date(
        title=_(u"Expiry date"),
        required=False,
        default=NULLDATE
    )

    credits = schema.Int(
        title=_(u"Credits"),
        description=_("Credits"),
        required=False,
        default=0,
    )


@indexer(IMemberService)
def userid(obj):
    return obj.Creator()
grok.global_adapter(userid, name="userid")


@indexer(IMemberService)
def serviceuid(obj):
    uuid = IUUID(obj.related_service.to_object)
    return uuid
grok.global_adapter(serviceuid, name="serviceuid")


class MemberService(dexterity.Item):
    grok.implements(IMemberService)
    

class SampleView(grok.View):
    grok.context(IMemberService)
    grok.require('zope2.View')
    
    # grok.name('view')
