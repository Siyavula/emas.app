import datetime
from DateTime import DateTime
from z3c.relationfield.relation import create_relation
from zope.component.hooks import getSite
from zope.component import queryUtility
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer

from emas.app.usercatalog import IUserCatalog
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

# list of services from siyavula.memberservices
service_from_id = {
    790567271: ('maths', 10),    # Maths Grade 10 Intelligent Practice
    790567279: ('maths', 11),    # Maths Grade 11 Intelligent Practice
    790567258: ('maths', 12),    # Maths Grade 12 Intelligent Practice
    790567266: ('science', 10),  # Science Grade 10 Intelligent Practice
    790567269: ('science', 11),  # Science Grade 11 Intelligent Practice
    790567257: ('science', 12),  # Science Grade 12 Intelligent Practice
    838326968: ('maths', 10),    # Maths Grade 10 Monthly Intelligent Practice
    838326969: ('maths', 11),    # Maths Grade 11 Monthly Intelligent Practice
    838326967: ('maths', 12),    # Maths Grade 12 Monthly Intelligent Practice
    838326965: ('science', 10),  # Science Grade 10 Monthly Intelligent Practice
    838326966: ('science', 11),  # Science Grade 11 Monthly Intelligent Practice
    838326964: ('science', 12),  # Science Grade 12 Monthly Intelligent Practice
}

service_subject_ids = dict(
    [(subject, [key for (key, value) in service_from_id.iteritems()
                if value[0] == subject]) for subject in ['maths', 'science']])


def onOrderPaid(order, event):
    """ Once the order is paid we create the memberservices.
    """
    if event.action == 'pay':
        portal = getToolByName(order, 'portal_url').getPortalObject()
        intids = queryUtility(IIntIds, context=portal)
        dao = MemberServicesDataAccess(portal)
        # we cannot use the authenticated user since an admin user might
        # trigger the workflow.
        memberid = order.userid 

        now = datetime.datetime.now().date()
        # grab the services from the orderitems
        for item in order.order_items():
            # try to find the memberservices based on the orderitem
            # related services.
            order_related_service = item.related_item.to_object
            related_service_ids = [intids.getId(order_related_service)]

            # filter out services that don't have subject or grade set,
            # eg. discounts
            service_purchased = item.related_item.to_object
            if not (service_purchased.grade and service_purchased.subject):
                continue

            # add the service siyavula.memberservices uses for trial access
            related_service_ids.append(
                service_subject_ids[order_related_service.subject][0]
            )
            memberservices = dao.get_memberservices(
                related_service_ids, memberid
            )

            tmpservices = []

            for ms in memberservices:
                related_service = ms.related_service(order)
                if (related_service.subject == service_purchased.subject and
                    related_service.access_path == \
                        service_purchased.access_path):
                    tmpservices.append(ms)

            # create a new memberservice if it doesn't exist
            if len(memberservices) == 0:
                mstitle = '%s for %s' % (order_related_service.title, memberid)
                props = {'memberid': memberid,
                         'title': mstitle,
                         'related_service_id': intids.getId(order_related_service),
                         'expiry_date': now,
                         'service_type': order_related_service.service_type}
                ms = dao.add_memberservice(**props)
                tmpservices.append(ms)

            # update the memberservices with info from the orderitem
            for ms in tmpservices:
                # NOTE: remove this when we remove siyavula.what
                if order_related_service.service_type == 'credit':
                    credits = ms.credits
                    credits += order_related_service.amount_of_credits
                    ms.credits = credits
                elif order_related_service.service_type == 'subscription':
                    # Always use the current expiry date if it is greater than
                    # 'now', since that gives the user everything he paid for.
                    # Only use 'now' if the related_service has already expired, so we
                    # don't give the user more than he paid for.
                    if now > ms.expiry_date:
                        ms.expiry_date = now
                    expiry_date = ms.expiry_date + datetime.timedelta(
                        order_related_service.subscription_period
                    )
                    ms.expiry_date = expiry_date
                dao.update_memberservice(ms)
            
            # if we have specific access groups add the user to those here.
            access_group = order_related_service.access_group
            if access_group:
                gt = getToolByName(order, 'portal_groups')
                # now add the member to the correct group
                gt.addPrincipalToGroup(memberid, access_group)


def memberServiceAdded(obj, event):
    service = obj.related_service.to_object
    intids = queryUtility(IIntIds, context=service)
    related_service_id = intids.getId(service)
    memberid = obj.memberid
    dao = MemberServicesDataAccess(obj)
    memberservices = dao.get_memberservices([related_service_id], memberid)

    if memberservices is not None and len(memberservices) > 0:
        raise RuntimeError(
            'Only one memberservice is allowed per purchasable service.'
            'This member (%s) already has a memberservice for '
            '%s.' %(obj.userid, service.Title())
        )


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
        ms = dao.add_memberservice(**props) 

    getUtility(IUserCatalog).index(obj)


def onMemberPropsUpdated(obj, event):
    getUtility(IUserCatalog).index(obj)


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
