import datetime
from z3c.relationfield.relation import create_relation
from zope.component.hooks import getSite

from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer

from emas.theme.browser.views import is_expert

from emas.app.browser.utils import member_services_for
from emas.app.browser.utils import member_services_for_subject
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
        msfolder = portal['memberservices']
        now = datetime.datetime.now().date()
        tmpservices = []

        # grab the services from the orderitems
        for item in order.order_items():
            # try to find the memberservices based on the orderitem
            # related services.

            service_purchased = item.related_item.to_object

            memberservices = member_services_for(
                portal, IUUID(service_purchased), userid
                )
            for ms in memberservices:
                active_service = ms.related_service.to_object
                if (active_service.subject == service_purchased.subject and
                    active_service.grade == service_purchased.grade and
                    active_service.access_path == \
                        service_purchased.access_path):
                    tmpservices.append(ms)

            # create a new memberservice if it doesn't exisst
            if len(tmpservices) == 0:
                mstitle = '%s for %s' % (service_purchased.title, userid)

                related_service = create_relation(
                    service_purchased.getPhysicalPath()
                    )
                props = {'title': mstitle,
                         'userid': userid,
                         'related_service': related_service,
                         'service_type': service_purchased.service_type
                         }

                ms = createContentInContainer(
                    msfolder,
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
                if service_purchased.service_type == 'credit':
                    credits = ms.credits
                    credits += service_purchased.amount_of_credits
                    ms.credits = credits
                elif service_purchased.service_type == 'subscription':
                    # Always use the current expiry date if it is greater than
                    # 'now', since that gives the user everything he paid for.
                    # Only use 'now' if the service has already expired, so we
                    # don't give the user more than he paid for.
                    if now > ms.expiry_date:
                        ms.expiry_date = now
                    expiry_date = ms.expiry_date + datetime.timedelta(
                        service_purchased.subscription_period
                    )
                    ms.expiry_date = expiry_date
                if ms.related_service.to_object.subscription_period < \
                   service_purchased.subscription_period:
                   ms.related_service = service_purchased
                ms.reindexObject()
            
            # if we have specific access groups add the user the those here.
            access_group = service_purchased.access_group
            if access_group:
                gt = getToolByName(order, 'portal_groups')
                # now add the member to the correct group
                gt.addPrincipalToGroup(order.userid, access_group)


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

    # fix up ownership (if manager created member service)
    if obj.userid not in obj.users_with_local_role('Owner'):
        pms = getToolByName(obj, 'portal_membership')
        pms.setLocalRoles(obj, [obj.userid], 'Owner')
        obj.reindexObject()



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
        'maths-grade10-monthly-practice',
        'maths-grade11-monthly-practice',
        'maths-grade12-monthly-practice',
        'science-grade10-monthly-practice',
        'science-grade11-monthly-practice',
        'science-grade12-monthly-practice',
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


def service_cost_updated(event):
    iface = event.record.interfaceName
    fname = event.record.fieldName
    price = event.newValue
    site = getSite()
    if not iface == 'emas.theme.interfaces.IEmasServiceCost':
        return
    
    if fname == 'practiceprice':
        for sid in ('maths-grade10-practice',
                    'maths-grade11-practice',
                    'maths-grade12-practice',
                    'science-grade10-practice',
                    'science-grade11-practice',
                    'science-grade12-practice'):
            service = site.products_and_services[sid]
            service.price = price
    elif fname == 'textbookprice':
        for sid in ('maths-grade10-textbook',
                    'maths-grade11-textbook',
                    'maths-grade12-textbook',
                    'science-grade10-textbook',
                    'science-grade11-textbook',
                    'science-grade12-textbook'):
            service = site.products_and_services[sid]
            service.price = price
