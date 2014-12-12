from AccessControl.Permissions import manage_users as ManageUsers
from zope.i18nmessageid import MessageFactory
from zope.app.component.hooks import getSite
from Products.PluggableAuthService import registerMultiPlugin
from Products.CMFPlone.utils import ToolInit

from emas.app.catalogtool import EMASCatalogTool
from emas.app.pas.portal import PortalAuthHelper,\
    manage_addPortalAuthHelperForm, manage_addPortalAuthHelper

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('emas.app')

# Register pas plugin
registerMultiPlugin(PortalAuthHelper.meta_type)

tools = (EMASCatalogTool,)

def initialize(context):
    # Register our custom catalog tool
    ToolInit('EMAS Catalog Tool',
             tools=tools,
             icon='tool.gif',
             ).initialize(context)

    # register pas plugin
    context.registerClass(PortalAuthHelper,
        permission=ManageUsers,
        constructors=(manage_addPortalAuthHelperForm, 
            manage_addPortalAuthHelper),
        visibility=None,
        icon='pas/portal.png')
