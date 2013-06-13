import datetime
from z3c.relationfield.relation import create_relation
from zope.component.hooks import getSite
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds

from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer

from emas.theme.browser.views import is_expert

from emas.app.browser.utils import qaservice_uuids
from emas.app.memberservice import MemberServicesDataAccess 


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
        dao = MemberServicesDataAccess(portal)
        # we cannot use the authenticated user since an admin user might
        # trigger the workflow.
        memberid = order.userid 

        now = datetime.datetime.now().date()
        # grab the services from the orderitems
        for item in order.order_items():
            # try to find the memberservices based on the orderitem
            # related services.
            related_service = item.related_item.to_object
            related_service_id = intids.getId(related_service)
            memberservices = dao.get_member_services([related_service_id], memberid)
            # create a new memberservice if it doesn't exisst
            if len(memberservices) == 0:
                mstitle = '%s for %s' % (related_service.title, memberid)
                props = {'memberid': memberid,
                         'title': mstitle,
                         'related_service_id': intids.getId(related_service),
                         'expiry_date': trialend,
                         'service_type': related_service.service_type}
                ms_id = dao.add_memberservice(**props)
                ms = dao.get_memberservice_by_primary_key(ms_id)
                tmpservices.append(ms)

            # update the memberservices with info from the orderitem
            for ms in tmpservices:
                if related_service.service_type == 'credit':
                    credits = ms.credits
                    credits += related_service.amount_of_credits
                    ms.credits = credits
                elif related_service.service_type == 'subscription':
                    # Always use the current expiry date if it is greater than
                    # 'now', since that gives the user everything he paid for.
                    # Only use 'now' if the related_service has already expired, so we
                    # don't give the user more than he paid for.
                    if now > ms.expiry_date:
                        ms.expiry_date = now
                    expiry_date = ms.expiry_date + datetime.timedelta(
                        related_service.subscription_period
                    )
                    ms.expiry_date = expiry_date
                dao.update_memberservice(ms)
            
            # if we have specific access groups add the user to those here.
            access_group = related_service.access_group
            if access_group:
                gt = getToolByName(order, 'portal_groups')
                # now add the member to the correct group
                gt.addPrincipalToGroup(memberid, access_group)


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
    
    pps = self.context.restrictedTraverse('@@plone_portal_state')
    memberid = pps.member().getId()
    dao = MemberServicesDataAccess(context)
    memberservices = dao.get_member_services(context, service_uids)
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

    pps = self.context.restrictedTraverse('@@plone_portal_state')
    memberid = pps.member().getId()
    dao = MemberServicesDataAccess(context)
    memberservices = dao.get_member_services(context, service_uids)
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
    products_and_services = portal._getOb('products_and_services')
    dao = MemberServicesDataAccess(obj)
    intids = queryUtility(IIntIds, context=obj)

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
        related_service = products_and_services[sid]
        mstitle = '%s for %s' % (related_service.title, memberid)
        props = {'memberid': memberid,
                 'title': mstitle,
                 'related_service_id': intids.getId(related_service),
                 'expiry_date': trialend,
                 'service_type': related_service.service_type}
        ms_id = dao.add_memberservice(**props) 


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
