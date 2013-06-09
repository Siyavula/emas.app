from sqlalchemy import *
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker, relation

# must come from environment; add to buildout soonest!
#postgresql[+driver]://<user>:<pass>@<host>/<dbname>
DSN='postgresql://emas:emas@localhost:5435/emas'
TWOPHASE=True
ENGINE = create_engine(DSN, convert_unicode=True)
EMAS_SESSION_MAKER = sessionmaker(bind=ENGINE,
                                  twophase=TWOPHASE,
                                  extension=ZopeTransactionExtension())
SESSION = scoped_session(EMAS_SESSION_MAKER)
