from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.registry
        import plone.resource
        import plone.app.theming
        import plone.app.folder
        import rhaptos.xmlfile
        import collective.topictree
        import webcouturier.dropdownmenu
        import emas.transforms
        import rhaptos.cnxmltransforms
        import rhaptos.compilation
        import upfront.shorturl
        import fullmarks.mathjax
        import siyavula.what
        import inqbus.plone.fastmemberproperties
        import emas.app

        self.loadZCML(package=plone.app.registry)
        self.loadZCML(package=plone.resource)
        self.loadZCML(package=plone.app.theming)
        self.loadZCML(package=plone.app.folder)
        self.loadZCML(package=rhaptos.xmlfile)
        self.loadZCML(package=collective.topictree)
        self.loadZCML(package=webcouturier.dropdownmenu)
        self.loadZCML(package=emas.transforms)
        self.loadZCML(package=rhaptos.cnxmltransforms)
        self.loadZCML(package=rhaptos.compilation)
        self.loadZCML(package=upfront.shorturl)
        self.loadZCML(package=fullmarks.mathjax)
        self.loadZCML(package=siyavula.what)
        self.loadZCML(package=inqbus.plone.fastmemberproperties)
        self.loadZCML(package=emas.app)


    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'emas.app:default')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='emas.app:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='emas.app:Functional',
    )
