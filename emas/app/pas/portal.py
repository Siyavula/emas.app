# Implement a pas plugin for the siyavula portal, using the auth and profile
# services.

import re
import json
import socket
from httplib import HTTPConnection
from urllib import quote
from zope.interface import Interface, alsoProvides
from App.special_dtml import DTMLFile
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from Products.PluggableAuthService.interfaces.plugins import \
    IExtractionPlugin, IAuthenticationPlugin, IChallengePlugin,\
    IPropertiesPlugin, IRolesPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

PROFILESERVER = 'localhost:6543'

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
    def getPropertiesForUser(self, user, request=None):
        """ Fetch user's properties from the profile service. """
        # Before going to the expensive step of talking to the profile
        # server, check that the userid at least looks like a uuid
        userid = user.getUserId()
        if not re.compile('^[0-9a-f-]+$').match(userid):
            return {}

        conn = HTTPConnection(self.profile_service)
        try:
            conn.request("GET", "/profile/read/%s" % userid)
        except socket.error:
            return {}
            
        result = conn.getresponse()
        if result.status == 200:
            try:
                data = json.loads(result.read())
            except ValueError:
                return {}
            if data:
                general = data.get('general', {})
                name = general.get('name', None) or ''
                surname = general.get('surname', None) or ''
                fullname = (name + ' ' + surname).strip()
                email = general.get('email', None) or ''
                properties = {
                    'fullname': fullname,
                    'email': email
                }
                emasdata = data.get('emas', {})
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

classImplements(PortalAuthHelper,
    IExtractionPlugin,
    IAuthenticationPlugin,
    IChallengePlugin,
    IPropertiesPlugin,
    IRolesPlugin)

InitializeClass(PortalAuthHelper)
