from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from emas.app.product import Product
from emas.app.product import IProduct
from emas.app import MessageFactory as _


vocab_service_types = SimpleVocabulary(
    [
     SimpleTerm(value=u'credit', title=_(u'Credit based')),
     SimpleTerm(value=u'subscription', title=_(u'Subscription based')),
    ]
)

vocab_grades = SimpleVocabulary(
    [
     SimpleTerm(value=u'grade10', title=_(u'Grade 10')),
     SimpleTerm(value=u'grade11', title=_(u'Grade 11')),
     SimpleTerm(value=u'grade12', title=_(u'Grade 12')),
    ]
)

vocab_subjects = SimpleVocabulary(
    [
     SimpleTerm(value=u'maths', title=_(u'Maths')),
     SimpleTerm(value=u'science', title=_(u'Science')),
    ]
)


class IService(IProduct):
    """
    An orderable service (e.g. intelligent practice)
    """
    service_type = schema.Choice(
        title=_(u"Service type"),
        vocabulary=vocab_service_types,
        required=False,
    )

    subscription_period = schema.Int(
        title=_(u"Subscription period"),
        required=False,
    )

    amount_of_credits = schema.Int(
        title=_(u"Amount of credits"),
        required=False,
    )

    grade = schema.Choice(
        title=_(u"Grade"),
        vocabulary=vocab_grades,
        required=True,
    )

    subject = schema.Choice(
        title=_(u"Subject"),
        vocabulary=vocab_subjects,
        required=True,
    )


class Service(Product):
    grok.implements(IService)
    

class SampleView(grok.View):
    grok.context(IService)
    grok.require('zope2.View')
    
    # grok.name('view')
