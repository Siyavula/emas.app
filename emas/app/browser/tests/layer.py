from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        self.addProfile('emas.theme:default')
        self.addProfile('emas.app:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
