from datetime import date
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID


service_mapping = {
    'qaservices' : {
        'general': [],
        'maths/grade-10'  :['products_and_services/maths-grade10-questions',
                           ],
        'maths/grade-11'  :['products_and_services/maths-grade11-questions',
                           ],
        'maths/grade-12'  :['products_and_services/maths-grade12-questions',
                           ],
        'science/grade-10':['products_and_services/science-grade10-questions',
                           ],
        'science/grade-11':['products_and_services/science-grade11-questions',
                           ],
        'science/grade-12':['products_and_services/science-grade12-questions',
                           ]
    },
    'practice_services' : {
        'general' : ['products_and_services/maths-grade10-practice',
                     'products_and_services/maths-grade11-practice',
                     'products_and_services/maths-grade12-practice',
                     'products_and_services/science-grade10-practice',
                     'products_and_services/science-grade11-practice',
                     'products_and_services/science-grade12-practice'
                    ]
    }
}


def qaservice_paths(self):
    return service_mapping.get('qaservices')

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


def paths_to_uuids(paths, context):
    uids = []
    for path in paths:
        obj = context.restrictedTraverse(path)
        if obj:
            uids.append(IUUID(obj))
    return uids


def qaservice_uuids(context):
    mapping = service_mapping.get('qaservices')
    service_paths = mapping.get('general')
    subject, grade = subject_and_grade(context)
    service_paths.extend(
        mapping.get('%s/%s' %(subject, grade), [])
    )
    return paths_to_uuids(service_paths, context)


def practice_service_uuids(context):
    mapping = service_mapping.get('practice_services')
    # at this stage we use only the general mappings since we don't have
    # practice services that are context specific in EMAS yet.
    service_paths = mapping.get('general')
    return paths_to_uuids(service_paths, context)


def member_services(context, service_uids):
    pmt = getToolByName(context, 'portal_membership')
    member = pmt.getAuthenticatedMember()
    query = {'portal_type': 'emas.app.memberservice',
             'memberid': member.getId(),
             'serviceuid': service_uids,
             'sort_on': 'expiry_date'
            }
    pc = getToolByName(context, 'portal_catalog')
    memberservices = [b.getObject() for b in pc(query)]
    return memberservices


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


def memberservice_expiry_date(context):
    expiry_date = None

    service_uids = qaservice_uuids(context)
    if service_uids is None or len(service_uids) < 1:
        return None 
    
    memberservices = member_services(context, service_uids)
    if len(memberservices) < 1:
        return  None

    for ms in memberservices:
        expiry_date = ms.expiry_date

    return expiry_date

def practice_service_expirydate(context):
    service_uids = practice_service_uuids(context)

    if service_uids is None or len(service_uids) < 1:
        return None
    
    memberservices = member_services(context, service_uids)
    if len(memberservices) < 1:
        return  None
    
    return memberservices[0].expiry_date

