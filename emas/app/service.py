from five import grok
from plone.directives import dexterity, form
from plone.indexer import indexer

from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName
from plone.app.z3cform.wysiwyg.widget import WysiwygFieldWidget

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
     SimpleTerm(value=u'grade-10', title=_(u'Grade 10')),
     SimpleTerm(value=u'grade-11', title=_(u'Grade 11')),
     SimpleTerm(value=u'grade-12', title=_(u'Grade 12')),
    ]
)

vocab_subjects = SimpleVocabulary(
    [
     SimpleTerm(value=u'maths', title=_(u'Maths')),
     SimpleTerm(value=u'science', title=_(u'Science')),
    ]
)

vocab_channels = SimpleVocabulary(
    [
     SimpleTerm(value=u'web', title=_(u'Web')),
     SimpleTerm(value=u'mobile', title=_(u'Mobile web')),
     SimpleTerm(value=u'mxit', title=_(u'MXit')),
    ]
)

@grok.provider(IContextSourceBinder)
def get_vocab_groups(context):
    gt = getToolByName(context, 'portal_groups')
    terms = []
   
    for group in gt.listGroups():
        id = group.getGroupId()
        name = group.getGroupName()
        terms.append(SimpleVocabulary.createTerm(id, name))
            
    return SimpleVocabulary(terms)


class IService(IProduct):
    """
    An orderable service (e.g. intelligent practice)
    """
    service_type = schema.Choice(
        title=_(u"Service type"),
        vocabulary=vocab_service_types,
        required=True,
    )

    subscription_period = schema.Int(
        title=_(u"Subscription period"),
        required=False,
        default=30,
    )

    amount_of_credits = schema.Int(
        title=_(u"Amount of credits"),
        required=False,
        default=20,
    )

    amount_of_moola = schema.Int(
        title=_(u"Amount of moola"),
        required=False,
        default=200,
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
    
    channels = schema.List(
        title = _(u"Delivery channel"),
        required = True,
        value_type = schema.Choice(vocabulary = vocab_channels),
        default = ['web', 'mobile'],
    )

    access_group = schema.Choice(
        title = _(u"Access groups"),
        required = False,
        source = get_vocab_groups,
        default = 'Members',
    )


@indexer(IService)
def grade(obj):
    return obj.grade
grok.global_adapter(grade, name="grade")


@indexer(IService)
def subject(obj):
    return obj.subject
grok.global_adapter(subject, name="subject")


@indexer(IService)
def channels(obj):
    return obj.channels
grok.global_adapter(channels, name="channels")


class Service(Product):
    grok.implements(IService)


class View(dexterity.DisplayForm):
    grok.context(IService)
    grok.require('zope2.View')
    #grok.name('view')
