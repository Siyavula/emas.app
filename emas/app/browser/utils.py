import hashlib


from urlparse import urlparse
from datetime import date, datetime, timedelta
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds



from emas.app.utilities import IVerificationCodeUtility

KEY_BASE = 'emas.app'


service_mapping = {
    'practice_services' : {
        'general' : ['products_and_services/maths-grade10-practice',
                     'products_and_services/maths-grade11-practice',
                     'products_and_services/maths-grade12-practice',
                     'products_and_services/maths-grade12-papers',
                     'products_and_services/science-grade10-practice',
                     'products_and_services/science-grade11-practice',
                     'products_and_services/science-grade12-practice',
                     'products_and_services/science-grade12-papers',
                     'products_and_services/maths-grade10-monthly-practice',
                     'products_and_services/maths-grade11-monthly-practice',
                     'products_and_services/maths-grade12-monthly-practice',
                     'products_and_services/science-grade10-monthly-practice',
                     'products_and_services/science-grade11-monthly-practice',
                     'products_and_services/science-grade12-monthly-practice',
                    ]
    }
}

SERVICE_IDS = [
    'maths-grade10-practice',
    'science-grade10-practice',
    'maths-grade11-practice',
    'science-grade11-practice',
    'maths-grade12-practice',
    'science-grade12-practice',
    'maths-grade10-monthly-practice',
    'maths-grade11-monthly-practice',
    'maths-grade12-monthly-practice',
    'science-grade10-monthly-practice',
    'science-grade11-monthly-practice',
    'science-grade12-monthly-practice',
]

"""
TODO: Move to a vocabulary or registry instead of hard coding here.
"""
SUBJECTS = [
    'maths',
    'science',
]


def get_subjects():
    return SUBJECTS


def get_subject_from_context(context):
    pps = context.restrictedTraverse('@@plone_portal_state')
    subject = pps.navigation_root().getId()
    return subject


def get_subject_from_path(path):
    """ We assume the path will start with the subject, since that is the way
        EMAS is configured.
        We can expect something like:
        /emas/maths/@@practice/grade-10
    """
    subject = None
    path = path.split('/')
    if len(path) > 1:
        if path[2] in get_subjects():
            subject = path[2]
    return subject


def get_grade_from_path(path):
    """ The path will might have a grade, because that is the way the EMAS foder
        structure works.
        We could have something like:
        /emas/maths/@@practice/grade-10
    """
    grade = None
    parts = path.split('/')
    token = '@@practice'
    if token in parts:
        startpos = parts.index(token)
        if startpos and len(parts) > startpos + 1:
            grade = parts[startpos+1]
    return grade


def subject_and_grade(context):
    """
        We trust in the structure of the content. Currently, this is
        /[subject]/[grade]/[content]

        Less than 4 elements means this was called on a context
        that does not have subject and grade as part of the path.
        We return the tuple ('none', 'none'), because there are no
        grades or subjects titled 'none'.
    """
    ppath = context.getPhysicalPath()
    if len(ppath) < 4:
        return ('none', 'none')
    return context.getPhysicalPath()[2:4]


def service_url(service):
    # XXX: fix urls to point to appropriate site hosting the service
    portal_url = service.restrictedTraverse('@@plone_portal_state').portal_url()
    grade = service.related_service.to_object.grade
    return '%s/@@practice/%s' %(portal_url, grade)


def member_credits(context):
    credits = 0

    service_uids = qaservice_uuids(context)
    if service_uids is None or len(service_uids) < 1:
        return 0

    memberservices = member_services(context, service_uids)
    if len(memberservices) < 1:
        return 0 

    for ms in memberservices:
        credits += ms.credits
    return credits


def annotate(obj, key, value):
    annotations = IAnnotations(obj)
    key = '%s.%s' %(KEY_BASE, key)
    annotations[key] = value


def get_annotation(obj, key):
    annotations = IAnnotations(obj)
    key = '%s.%s' %(KEY_BASE, key)
    return annotations.get(key, '')


def compute_vcs_response_hash(props, md5key):
    keys = ("p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10", "p11",
            "p12", "pam", "m_1", "m_2", "m_3", "m_4", "m_5", "m_6", "m_7",
            "m_8", "m_9", "m_10", "CardHolderIpAddr", "MaskedCardNumber",
            "TransactionType",)

    tmpstr = ''
    for key in keys:
        tmpstr = tmpstr + props.get(key,'')
    tmpstr = tmpstr + md5key

    m = hashlib.md5()
    m.update(tmpstr)
    return m.hexdigest()


def get_discount_items(context, selected_items): 
    pps = context.restrictedTraverse('@@plone_portal_state')
    portal = pps.portal()
    products_and_services = portal.products_and_services

    discount_items = {}
    deals = {'maths-grade10-discount'   :['maths-grade10-practice',
                                          'maths-grade10-textbook'],
             'science-grade10-discount' :['science-grade10-practice',
                                          'science-grade10-textbook'],
             'maths-grade11-discount'   :['maths-grade11-practice',
                                          'maths-grade11-textbook'],
             'science-grade11-discount' :['science-grade11-practice',
                                          'science-grade11-textbook'],
             'maths-grade12-discount'   :['maths-grade12-practice',
                                          'maths-grade12-textbook'],
             'science-grade12-discount' :['science-grade12-practice',
                                          'science-grade12-textbook'], }
    
    selected_items = set(selected_items.keys())
    for discount_id, items in deals.items():
        deal_items = \
            set([products_and_services._getOb(item) for item in items])

        common_items = selected_items.intersection(deal_items)
        if len(common_items) == len(deal_items):
            discount_service = products_and_services._getOb(discount_id)
            quantity = discount_items.get(discount_service.getId(), 0) +1
            discount_items[discount_service] = quantity

    return discount_items


def get_display_items_from_request(context):
    """
    The submitted form data looks like this:
        {'order.form.submitted': 'true',
        'prod_practice_book': 'Practice,Textbook',
        'practice_subjects': 'Maths,Science',
        'submit': '1',
        'practice_grade': 'Grade 10'}
    """
    request = context.get('request', context.REQUEST)
    display_items = {}
    
    grade = request.form.get('grade', '')
    prod_practice_book = request.form.get('prod_practice_book', '')
    subjects = request.form.get('subjects', '')
    for subject in subjects.split(','):
        for item in prod_practice_book.split(','):
            # e.g. subject-grade-[practice | questions | textbook]
            sid = '%s-%s-%s' %(subject, grade, item)
            sid = sid.replace(' ', '-').lower()
            quantity = display_items.get(sid, 0) +1
            service = products_and_services._getOb(sid)
            display_items[service] = quantity
            
    return display_items


def get_display_items_from_order(order):
    display_items = []
    # it is a LazyMap, we slice it to get the full objects
    orderitems = order.order_items()
    orderitems = dict(
        (item.related_item.to_object, item.quantity)
        for item in orderitems
    )
    discount_items = get_discount_items(order, orderitems)

    discount_items = set(discount_items.keys())
    orderitems = set(orderitems.keys())
    
    items = orderitems.difference(discount_items)
    uuids = [IUUID(item) for item in items]
    items = member_services(order, uuids)
    display_items = [i for i in items \
                     if i.related_service.to_object.getId() in SERVICE_IDS]
    return display_items 


def get_paid_orders_for_member(context, memberid):
    query = {'portal_type': 'emas.app.order',
             'userid': memberid,
             'review_state': 'paid'
            }
    pc = getToolByName(context, 'portal_catalog')
    brains = pc(query)
    return [b.getObject() for b in brains]


def generate_verification_code(order):
    vcu = getUtility(IVerificationCodeUtility, context=order)
    return vcu.generate(order)


def is_unique_verification_code(context, verification_code):
    vcu = getUtility(IVerificationCodeUtility, context=order)
    return vcu.is_unique(verification_code)
