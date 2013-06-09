from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

from zope.interface import Interface, implements

class IMemberService(Interface):
    """
        Marker interface.
    """


Base = declarative_base()
class MemberService(Base):
    
    implements(IMemberService)

    __tablename__ = 'memberservices'

    id                 = Column('memberservice_id', Integer, primary_key=True)
    userid             = Column('userid', String(100))
    title              = Column('title', String(100))
    related_service_id = Column('related_service_id', Integer)
    expiry_date        = Column('expiry_date', Date)
    credits            = Column('credits', Integer)
    service_type       = Column('service_type', String(100))
