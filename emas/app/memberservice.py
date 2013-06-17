from datetime import datetime
import transaction

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    create_engine,
    or_,
    and_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from zope.sqlalchemy import ZopeTransactionExtension

from zope.interface import Interface, implements
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds

from emas.app.interfaces import IMemberServiceDataAccess


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


class MemberServicesDataAccess(object):

    implements(IMemberServiceDataAccess)

    def __init__(self, context):
        self.context = context
        self.intids = queryUtility(IIntIds, context=context)
    
    def get_all_memberservices(self):
        """ Fetches all memberservices regardless of memberid, grade or subject.
            Useful for full export of all current memberservices or listing views.
        """
        session = SESSION()
        return session.query(MemberService).all()

    def get_memberservices(self, service_uids, memberid):
        """ Fetches all memberservices for a specfic member.
            Ignores grade and subject.
            Ignores expiry dates.
        """
        session = SESSION()
        or_clause = or_()
        for s_id in service_uids:
            or_clause.append(MemberService.related_service_id == s_id)

        result = session.query(MemberService).filter(or_clause).filter(
            MemberService.memberid==memberid)

        return result.all()

    def get_memberservices_by_subject(self, memberid, subject):
        """ Fetches all memberservices for a specific member.
            Ignores expiry dates.
            Filters on subject.
        """
        memberservices = []
        session = SESSION()
        result = session.query(MemberService).filter(
            MemberService.memberid == memberid)
        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.subject == subject:
                memberservices.append(ms)

        return memberservices

    def get_memberservices_by_grade(self, memberid, grade):
        """ Fetches all memberservices for a specific member.
            Ignores expiry dates.
            Filters on grade.
        """
        memberservices = []
        session = SESSION()
        result = session.query(MemberService).filter(
            MemberService.memberid == memberid)
        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.grade == grade:
                memberservices.append(ms)

        return memberservices

    def get_memberservices_by_subject_and_grade(self, memberid, subject, grade):
        """ Fetches all memberservices for a specific member.
            Ignores expiry dates.
            Filters on subject and grade.
        """
        memberservices = []

        session = SESSION()
        result = session.query(MemberService).filter(
            MemberService.memberid == memberid)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.grade == grade and \
               related_service.subject == subject:

                memberservices.append(ms)

        return memberservices

    def get_active_memberservices(self, memberid):
        """ Fetches only active memberservices for a given member.
            Ignores subject and grade.
        """
        now = datetime.now().date()
        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date >= now)
        result = session.query(MemberService).filter(and_clause)
        return result.all()

    def get_active_memberservices_by_subject(self, memberid, subject):
        """ Fetches only active memberservices for a given member.
            Filters on subject.
        """
        now = datetime.now().date()
        memberservices = []

        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date >= now)
        result = session.query(MemberService).filter(and_clause)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.subject == subject:
                memberservices.append(ms)

        return memberservices

    def get_active_memberservices_by_grade(self, memberid, grade):
        """ Fetches only active memberservices for a given member.
            Filters on grade.
        """
        now = datetime.now().date()
        memberservices = []

        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.grade == grade,
                          MemberService.expiry_date >= now)

        result = session.query(MemberService).filter(and_clause)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.grade == grade:
                memberservices.append(ms)

        return memberservices

    def get_active_memberservices_by_subject_and_grade(self, memberid, subject, grade):
        """ Fetches all active memberservices for a specific member.
            Filters on subject and grade.
        """
        now = datetime.now().date()
        session = SESSION()

        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date >= now)
        result = session.query(MemberService).filter(and_clause)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.grade == grade and \
               related_service.subject == subject:

                memberservices.append(ms)

        return memberservices

    def get_expired_memberservices(self, memberid):
        """ Fetches only expired memberservices for a given member.
            Ignores subject and grade.
        """
        now = datetime.now().date()
        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date < now)

        result = session.query(MemberService).filter(and_clause)

        return result.all()

    def get_expired_memberservices_by_subject(self, memberid, subject):
        """ Fetches only expired memberservices for a given member.
            Filters on subject.
        """
        now = datetime.now().date()
        memberservices = []

        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date < now)
        result = session.query(MemberService).filter(and_clause)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.subject == subject:

                memberservices.append(ms)

        return memberservices

    def get_expired_memberservices_by_grade(self, memberid, grade):
        """ Fetches only expired memberservices for a given member.
            Filters on grade.
        """
        now = datetime.now().date()
        memberservices = []

        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date < now)
        result = session.query(MemberService).filter(and_clause)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.grade == grade:

                memberservices.append(ms)

        return memberservices

    def get_expired_memberservices_by_subject_and_grade(self, memberid, subject, grade):
        """ Fetches all expired memberservices for a specific member.
            Filters on subject and grade.
        """
        now = datetime.now().date()
        memberservices = []

        session = SESSION()
        and_clause = and_(MemberService.memberid == memberid,
                          MemberService.expiry_date < now)
        result = session.query(MemberService).filter(and_clause)

        for ms in result.all():
            related_service = self.related_service(ms)
            if related_service and related_service.grade == grade and \
               related_service.subject == subject:

                memberservices.append(ms)

        return memberservices

    def get_memberservice_by_primary_key(self, memberservice_id):
        """ Utility method.
            Useful if you know what the persistent store primary key is and just
            want to get that specific memberservice.
        """
        now = datetime.now().date()
        session = SESSION()
        memberservices = session.query(MemberService).filter(
            MemberService.id == memberservice_id).all()
        return memberservices and memberservices[0] or None

    def add_memberservice(self, memberid, title, related_service_id, expiry_date,
                          credits=0, service_type="subscription"):
        """ Adds a memberservice to the persistent store.
            Sets all given attributes.
            Returns the primary key of the new memberservice.
        """
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

    def update_memberservice(self, memberservice):
        """ Updates and existing memberservice.
            Returns the primary key of the update memberservice.
        """
        session = SESSION()
        ms = session.merge(memberservice)
        session.flush()
        ms_id = memberservice.id
        transaction.commit()
        return ms_id

    def delete_memberservice(self, memberservice):
        """ Deletes a given memberservice from the persistent store.
        """
        session = SESSION()
        session.delete(memberservice)
        transaction.commit()
    
    def related_service(self, memberservice):
        return self.intids.getObject(memberservice.related_service_id)
