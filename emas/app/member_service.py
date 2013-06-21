from datetime import datetime, date, timedelta
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

from emas.app.service import vocab_service_types
from emas.app import MessageFactory as _


NULLDATE = date(1970, 01, 01)
SUBSCRIPTION = 'subscription'
CREDITS = 'credits'

class IMemberService(form.Schema):
    """
    An object that describes the services or products a member bought.
    """

    userid = schema.TextLine(
        title=_(u"User id"),
        required=True,
    )

    related_service = RelationChoice(
        title=_(u'label_related_service', default=u'Related Service'),
        source=ObjPathSourceBinder(
          object_provides='emas.app.product.IProduct'),
        required=True,
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

    service_type = schema.Choice(
        title=_(u"Service type"),
        vocabulary=vocab_service_types,
        required=True,
    )


@indexer(IMemberService)
def userid(obj):
    return obj.userid
grok.global_adapter(userid, name="userid")


@indexer(IMemberService)
def serviceuid(obj):
    uuid = IUUID(obj.related_service.to_object)
    return uuid
grok.global_adapter(serviceuid, name="serviceuid")


@indexer(IMemberService)
def subject(obj):
    return obj.related_service.to_object.subject
grok.global_adapter(subject, name="subject")


@indexer(IMemberService)
def expiry_date(obj):
    return obj.expiry_date
grok.global_adapter(expiry_date, name="expiry_date")


class MemberService(dexterity.Item):
    grok.implements(IMemberService)
    
    def is_enabled(self):
        """ 
            check expiry date, if it is greater than now, enabled = True
            check credits, if is greater than 0, enabled = True
        """
        enabled = False
        st = self.service_type
        if st == SUBSCRIPTION:
            now = date.today()
            enabled = now <= self.expiry_date 
        else:
            enabled = self.credits > 0
        return enabled

    def is_similar_to(self, other):
        attrs = ['grade', 'subject', 'access_path']
        for attr in attrs:
            self_attr = getattr(self.related_service.to_object, attr, None)
            other_attr = getattr(other.related_service.to_object, attr, None)
            if self_attr != other_attr:
                return False
        return True
    
    def merge_with(self, other):
        now = datetime.now().date()
        delta = other.expiry_date - now
        if delta.days > 0:
            self.expiry_date = self.expiry_date + delta
        self_subs_period = self.related_service.to_object.subscription_period
        other_subs_period = other.related_service.to_object.subscription_period
        if other_subs_period > self_subs_period:
            self.related_service = other.related_service
        return self

    def merge_memberservices(self, memberservices):
        if not memberservices or len(memberservices) < 2:
            return memberservices

        other = memberservices.pop(0)
        for memberservice in memberservices:
            if memberservice.is_similar_to(other):
                memberservice.merge_with(other)
        return self.merge_memberservices(memberservices) 


class SampleView(grok.View):
    grok.context(IMemberService)
    grok.require('zope2.View')
    
    # grok.name('view')
