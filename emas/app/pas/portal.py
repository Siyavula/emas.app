# Implement a pas plugin for the siyavula portal, using the auth and profile
# services.

import re
import json
import socket
from httplib import HTTPConnection
from urllib import quote

from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError

from zope.interface import Interface, alsoProvides
from App.special_dtml import DTMLFile
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from Products.PluggableAuthService.interfaces.plugins import \
    IExtractionPlugin, IAuthenticationPlugin, IChallengePlugin,\
    IPropertiesPlugin, IRolesPlugin, IUserEnumerationPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

PROFILESERVER = 'postgresql:///siyavula'

class IAuthToken(Interface):
    """ Marker interface for request. """

def manage_addPortalAuthHelper(self, id, title='',
        RESPONSE=None):
    """ Publish me. """
    o = PortalAuthHelper(id, title)
    self._setObject(o.getId(), o)
    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addPortalAuthHelperForm = DTMLFile(
    "PortalAuthHelperForm", globals())

# Our regex also accepts a 5 at the start of the third group. That's not valid
# uuid4, but for some reason I have 131133 users with such a uuid right now.
uuidre = re.compile(
    '[0-9a-f]{8}-[0-9a-f]{4}-[45][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}')
def is_uuid4(s):
    return uuidre.match(s) is not None

class reify(object):
    """
    Put the result of a method which uses this (non-data)
    descriptor decorator in the instance dict after the first call,
    effectively replacing the decorator with an instance variable.
    
    Shamelessly stolen from pyramid.
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val

def graceful_recovery(wrapped):
    def wrapper(self, *args, **kwargs):
        try:
            return wrapped(self, *args, **kwargs)
        except SQLAlchemyError, e:
            self._v_Session().rollback()
            raise e
    return wrapper

Base = declarative_base()

class UserIdentifier(Base):
    """ This is a subset of the real user_identifiers table, just enough to
        do what we need to do. """
    __tablename__ = "user_identifiers"

    internal_user_id = Column(
        Integer, ForeignKey(
            'users.internal_user_id', ondelete='CASCADE'), index=True)
    field_name = Column(String, nullable=False)
    field_value = Column(String, primary_key=True)

class User(Base):
    """ This is a subset of the real User table, just enough to do what
        we need to do. """
    __tablename__ = "users"

    internal_user_id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    identifiers = relationship(UserIdentifier,
        backref='users')

class UserProfileGeneral(Base):
    """ General profile table. """
    __tablename__ = 'user_profile_general'
    uuid = Column(String, primary_key=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    username = Column(String, index=True, unique=True, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    telephone = Column(String, index=True, unique=True, nullable=True)

class UserProfile(Base):
    """ Extra profile information. """
    __tablename__ = 'user_profile'
    uuid = Column(String, primary_key=True)
    user_profile = Column(String)

class PortalAuthHelper(BasePlugin):
    """ Multi-plugin for managing plone running behind siyavula proxy. """
    meta_type = 'Portal Auth Helper'
    security = ClassSecurityInfo()
    _properties = ({
        'id': 'profile_service',
        'type': 'string',
        'mode': 'w',
        'label': 'A server/port in the format hostname:port'},)
    profile_service = PROFILESERVER

    @reify
    def _v_Session(self):
        engine = create_engine(self.profile_service)
        factory = scoped_session(sessionmaker())
        factory.configure(bind=engine)
        return factory

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    # IExtractionPlugin
    #     Return mapping with login, password. Passed to IAuthenticationPlugin.
    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ Check the header to see if we're handling a request from the
            portal. Then extract the required details. """
        # Get X-Siyavula-Portal-UUID header from request
        uuid = request.get_header('x-siyavula-portal-uuid')
        if uuid is not None:
            alsoProvides(request, IAuthToken)
            return {
                'uuid': uuid
            }
        return {}

    # IAuthenticationPlugin
    #     (login, password) -> (userid, login)
    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """ If our own extractCredentials found the proxy headers, look up that
            user in the auth service and return the required login. """
        # Look up the user in the auth service.
        # Legacy users will have a username identifier, use that.
        # New users simply use their uuid.
        if not IAuthToken.providedBy(self.REQUEST):
            return None
        login = credentials['uuid']
        return login, login

    # IChallengePlugin
    #     When user not logged in, send him to portal login page.
    security.declarePrivate('challenge')
    def challenge(self, request, response):
        """ If the user is not logged in, send him to the relevant place. """
        proxy = request.get_header('x-siyavula-portal-proxy')
        if proxy is not None:
            came_from = request.get('ACTUAL_URL', '')
            redir = proxy + '/sign-in'
            if came_from:
                redir += '?came_from=' + quote(came_from)
            response.redirect(redir, lock=1)
            response.setHeader('Expires', 'Sat, 01 Jan 2000 00:00:00 GMT')
            response.setHeader('Cache-Control', 'no-cache')
            return 1
        return 0

    # IPropertiesPlugin
    #     Fetch properties from profile service.
    security.declarePrivate('getPropertiesForUser')
    @graceful_recovery
    def getPropertiesForUser(self, user, request=None):
        """ Fetch user's properties from the profile service. """
        # Before going to the expensive step of talking to the profile
        # server, check that the userid at least looks like a uuid
        userid = user.getUserId()
        if not is_uuid4(userid):
            return {}

        general = self._v_Session().query(UserProfileGeneral).filter(
            UserProfileGeneral.uuid == userid).first()
        extra = self._v_Session().query(UserProfile).filter(
            UserProfile.uuid == userid).first()

        if general:
            name = general.name or ''
            surname = general.surname or ''
            properties = {
                'fullname': (name + ' ' + surname).strip(),
                'email': general.email or ''
            }

            # Parse the extra data and add it on
            try:
                extra = json.loads(extra.user_profile)
            except ValueError:
                extra = {}
            emasdata = extra.get('emas', {})
            for p in ('school', 'province'):
                if p in emasdata:
                    properties[p] = emasdata[p] or ''

            return properties

        return {}

    # IRolesPlugin plugin
    #   Assign the 'Member' role to authenticated people
    def getRolesForPrincipal(self, principal, request=None):
        if request and IAuthToken.providedBy(request):
            return ('Member',)
        return ()

    # IUserEnumerationPlugin plugin
    @graceful_recovery
    def enumerateUsers(self, id=None, login=None, exact_match=False,
            sort_by=None, max_results=None, **kw):
        if exact_match:
            # This is here only so getMemberById can work, so we don't care
            # about other searches. At least until further notice.
            if id and is_uuid4(id):
                users = self._v_Session().query(User).filter(
                    User.user_id == id).all()

                matched = []
                for user in users:
                    identifiers = user.identifiers
                    matched.append({
                        'id': user.user_id,
                        'login': len(identifiers) and \
                            identifiers[0].field_value or \
                            user.user_id,
                        'plugin_id': self.getId(),
                        'editurl': ''})
            elif login:
                identifiers = self._v_Session().query(UserIdentifier).filter(
                    UserIdentifier.field_value == login).all()
                matched = [{
                    'id': identifier.users.user_id,
                    'login': identifier.field_value,
                    'plugin_id': self.getId(),
                    'editurl': ''} for identifier in identifiers]
            else:
                return ()
                    
            return tuple(matched)
            
        return ()
        

classImplements(PortalAuthHelper,
    IExtractionPlugin,
    IAuthenticationPlugin,
    IChallengePlugin,
    IPropertiesPlugin,
    IRolesPlugin,
    IUserEnumerationPlugin)

InitializeClass(PortalAuthHelper)
