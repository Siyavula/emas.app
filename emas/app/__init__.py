from zope.i18nmessageid import MessageFactory
from zope.app.component.hooks import getSite
from Products.CMFPlone.utils import ToolInit

from emas.app.catalogtool import EMASCatalogTool

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('emas.app')

tools = (EMASCatalogTool,)

def initialize(context):
    # Register our custom catalog tool
    ToolInit('EMAS Catalog Tool',
             tools=tools,
             icon='tool.gif',
             ).initialize(context)
