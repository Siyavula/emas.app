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


def orderAdded(order, event):
    """ Set the userid
    """
    member = order.restrictedTraverse('@@plone_portal_state').member()
    order.userid = member.getId()
    order.date_ordered = datetime.datetime.now()


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
        pps = order.restrictedTraverse('@@plone_portal_state')
        portal = pps.portal()
        # we cannot use the authenticated user since an admin user might
        # trigger the workflow.
        userid = order.userid 

        memberservices = portal['memberservices']
        ms_path = '/'.join(memberservices.getPhysicalPath())

        pc = getToolByName(portal, 'portal_catalog')
        query = {'portal_type': 'memberservice',
                 'userid'   : userid,
                 'path'       : ms_path}
        
        tmpservices = []
        now = datetime.datetime.now()
        # grab the services from the orderitems
        for item in order.order_items():
            # try to find the memberservices based on the orderitem related services.
            service = item.related_item.to_object
            uuid = IUUID(service)
            query['serviceuid'] = uuid
            brains = pc(query)
            tmpservices.extend([b.getObject() for b in brains])

            # create new memberservices if not found
            if brains is None or len(brains) < 1:
                msid = memberservices.generateUniqueId(
                            type_name='emas.app.memberservice')

                ms = memberservices.invokeFactory(
                    type_name='emas.app.memberservice',
                    id=msid,
                    title=msid,
                    userid=userid,
                    related_service=create_relation(service.getPhysicalPath()),
                    service_type = service.service_type,
                )
                ms = memberservices._getOb(msid)
                # give the order owner permissions on the new memberservice, or
                # we wont' be able to find the memberservices for this user
                pms.setLocalRoles(ms, order.userid, 'Owner')
                tmpservices.append(ms)

            # update the memberservices with info from the orderitem
            for ms in tmpservices:
                if service.service_type == 'credit':
                    ms.credits = service.amount_of_credits
                elif service.service_type == 'subscription':
                    expiry_date = now + datetime.timedelta(
                                            service.subscription_period)
                    ms.expiry_date = expiry_date
