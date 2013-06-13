import transaction

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    create_engine,
    or_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from zope.sqlalchemy import ZopeTransactionExtension

from zope.interface import Interface, implements


# must come from environment; add to buildout soonest!
#postgresql[+driver]://<user>:<pass>@<host>/<dbname>
DSN='postgresql://emas:emas@localhost:5435/emas'
TWOPHASE=True
ENGINE = create_engine(DSN, convert_unicode=True)
EMAS_SESSION_MAKER = sessionmaker(bind=ENGINE,
                                  twophase=TWOPHASE,
                                  extension=ZopeTransactionExtension())
SESSION = scoped_session(EMAS_SESSION_MAKER)


class IMemberService(Interface):
    """
        Marker interface.
    """


Base = declarative_base()
class MemberService(Base):
    
    implements(IMemberService)

    __tablename__ = 'memberservices'

    id                 = Column('memberservice_id', Integer, primary_key=True)
    memberid           = Column('memberid', String(100))
    title              = Column('title', String(100))
    related_service_id = Column('related_service_id', Integer)
    expiry_date        = Column('expiry_date', Date)
    credits            = Column('credits', Integer)
    service_type       = Column('service_type', String(100))


def add_memberservice(memberid, title, related_service_id, expiry_date,
                      credits=0, service_type="subscription"):

    ms = MemberService(memberid=memberid,
                       title=title,
                       related_service_id=related_service_id,
                       expiry_date=expiry_date,
                       credits=credits,
                       service_type=service_type)
    session = SESSION()
    session.add(ms)
    # make sure this object in in the db without disassociating it from the 
    # session
    session.flush()
    # get the newly created primary key
    ms_id = ms.id
    # commit the transaction so it is available to everyone else
    transaction.commit()
    # return the id, so any calling code can immediately fetch the object
    # from the db.
    return ms_id

def update_memberservice(memberservice):
    session = SESSION()
    ms = session.merge(memberservice)
    session.flush()
    ms_id = memberservice.id
    transaction.commit()
    return ms_id

def delete_memberservice(memberservice):
    session = SESSION()
    session.delete(memberservice)
    transaction.commit()

def get_memberservices_by_memberid(memberid):
    session = SESSION()
    memberservices = session.query(MemberService).filter_by(
        memberid = memberid).all()
    return memberservices

def get_memberservice_by_primary_key(id):
    session = SESSION()
    memberservices = session.query(MemberService).filter_by(
        id = memberservice_id).all()
    return memberservices[0]

def member_services(context, service_uids):
    session = SESSION()
    return session.query(MemberService).all()

    pmt = getToolByName(context, 'portal_membership')
    member = pmt.getAuthenticatedMember()
    today = datetime.today().date()
    query = {'portal_type': 'emas.app.memberservice',
             'userid': member.getId(),
             'serviceuid': service_uids,
             'expiry_date': {'query':today, 'range':'min'}
            }
    pc = getToolByName(context, 'portal_catalog')
    memberservices = [b.getObject() for b in pc(query)]
    return memberservices

def member_services_for(context, service_uids, memberid):
    session = SESSION()
    or_clause = or_()
    for s_id in service_uids:
        or_clause.append(MemberService.related_service_id == s_id)
    result = session.query(MemberService).filter(or_clause).filter(
        MemberService.memberid==memberid)
    return result.all()


