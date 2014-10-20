from Globals import InitializeClass
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFPlone.CatalogTool import CatalogTool

class EMASCatalogTool(CatalogTool):
    
    id = 'order_catalog'
    meta_type = 'EMAS Catalog Tool'

    def __init__(self):
        ZCatalog.__init__(self, self.getId())

InitializeClass(EMASCatalogTool)
