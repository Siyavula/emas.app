import datetime

from zope.component import createObject
from z3c.relationfield.relation import create_relation

from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.permission import ModifyConstrainTypes
from Products.ATContentTypes.permission import ModifyViewTemplate
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.lib.constraintypes import ENABLED
from plone.dexterity.utils import createContentInContainer

from emas.theme.browser.views import is_expert

from emas.app.browser.utils import member_services
from emas.app.browser.utils import qaservice_uuids


def orderItemAdded(item, event):
    """ Calculate the total and set the price at purchase time.
    """
    _setOrderItemPriceAndTotal(item)


def orderItemUpdated(item, event):
    """ Calculate the total and set the price after an update.
    """
    _setOrderItemPriceAndTotal(item)


def _setOrderItemPriceAndTotal(item):
    price = item.price or item.related_item.to_object.price
    item.price = price
    item.total = item.quantity * item.price


def onOrderPaid(order, event):
    """ Once the order is paid we create the memberservices.
    """
    if event.action == 'pay':
        pms = getToolByName(order, 'portal_membership')
        portal = getToolByName(order, 'portal_url').getPortalObject()
        # we cannot use the authenticated user since an admin user might
        # trigger the workflow.
        userid = order.userid 

        memberservices = portal['memberservices']
        ms_path = '/'.join(memberservices.getPhysicalPath())

        pc = getToolByName(portal, 'portal_catalog')
        query = {'portal_type': 'emas.app.memberservice',
                 'userid'   : userid,
                 'path'       : ms_path}
        
        now = datetime.datetime.now().date()
        # grab the services from the orderitems
        for item in order.order_items():
            # try to find the memberservices based on the orderitem
            # related services.
            service = item.related_item.to_object
            uuid = IUUID(service)
            query['serviceuid'] = uuid
            brains = pc(query)
            tmpservices = [b.getObject() for b in brains]

            # create a new memberservice if it doesn't exisst
            if len(brains) == 0:
                mstitle = '%s for %s' % (service.title, userid)

                related_service = create_relation(service.getPhysicalPath())
                props = {'title': mstitle,
                         'userid': userid,
                         'related_service': related_service,
                         'service_type': service.service_type
                         }

                ms = createContentInContainer(
                    memberservices,
                    'emas.app.memberservice',
                    False,
                    **props
                )

                # give the order owner permissions on the new memberservice, or
                # we wont' be able to find the memberservices for this user
                ms.manage_setLocalRoles(order.userid, ('Owner',))
                tmpservices.append(ms)

            # update the memberservices with info from the orderitem
            for ms in tmpservices:
                if service.service_type == 'credit':
                    credits = ms.credits
                    credits += service.amount_of_credits
                    ms.credits = credits
                elif service.service_type == 'subscription':
                    # Always use the current expiry date if it is greater than
                    # 'now', since that gives the user everything he paid for.
                    # Only use 'now' if the service has already expired, so we
                    # don't give the user more than he paid for.
                    if now > ms.expiry_date:
                        ms.expiry_date = now
                    expiry_date = ms.expiry_date + datetime.timedelta(
                        service.subscription_period
                    )
                    ms.expiry_date = expiry_date
                ms.reindexObject()


def questionAsked(obj, event):
    """ Deduct a credit when a question is asked
    """
    if is_expert(obj):
        return

    context = obj.relatedContent.to_object

    service_uids = qaservice_uuids(context)
    # there are no services so the user cannot pay for any.
    if service_uids is None or len(service_uids) < 1:
        return

    memberservices = member_services(context, service_uids)
    if len(memberservices) < 1:
        raise RuntimeError("The user has no credits.")
    else:
        credits = memberservices[0].credits - 1
        memberservices[0].credits = credits


def questionDeleted(obj, event):
    """ Add a credit when a question is deleted.
    """
    if is_expert(obj):
        return

    context = obj.relatedContent.to_object

    service_uids = qaservice_uuids(context)
    if service_uids is None or len(service_uids) < 1:
        return

    memberservices = member_services(context, service_uids)
    if len(memberservices) < 1:
        raise RuntimeError("The user has no credits.")
    else:
        credits = memberservices[0].credits + 1
        memberservices[0].credits = credits


def memberServiceAdded(obj, event):
    service = obj.related_service.to_object
    obj_path = '/'.join(obj.getPhysicalPath())

    query = {'portal_type': 'emas.app.memberservice',
             'userid': obj.userid,
             'serviceuid': IUUID(service),
            }
    pc = getToolByName(service, 'portal_catalog')
    # exclude the current obj based on its path
    brains = [b for b in pc(query) if b.getPath() != obj_path]
    if brains is not None and len(brains) > 0:
        raise RuntimeError(
            'Only one memberservice is allowed per purchasable service.'
            'This member (%s) already has a memberservice for '
            '%s.' %(obj.userid, service.Title())
        )


def onMemberJoined(obj, event):
    memberid = obj.getId()
    portal = obj.restrictedTraverse('@@plone_portal_state').portal()
    pms = getToolByName(portal, 'portal_membership')
    products_and_services = portal._getOb('products_and_services')
    memberservices = portal._getOb('memberservices')

    # 30 days free trial with 2 questions
    today = datetime.date.today()
    trialend = today + datetime.timedelta(days=30)
    intelligent_practice_services = (
        'maths-grade10-practice',
        'maths-grade11-practice',
        'maths-grade12-practice',
        'science-grade10-practice',
        'science-grade11-practice',
        'science-grade12-practice',
    )

    for sid in intelligent_practice_services:
        service = products_and_services[sid]
        service_relation = create_relation(service.getPhysicalPath())
        mstitle = '%s for %s' % (service.title, memberid)
        props = {'title': mstitle,
                 'userid': memberid,
                 'related_service': service_relation,
                 'service_type': service.service_type}

        ms = createContentInContainer(
            memberservices,
            'emas.app.memberservice',
            False,
            **props
        )
        ms.expiry_date = trialend 
        ms.manage_setLocalRoles(memberid, ('Owner',))
        ms.reindexObject()
