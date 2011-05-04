from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
# from plone.testing import z2

from zope.configuration import xmlconfig

class MemberApprovalTestSuite(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.memberapproval
        xmlconfig.file('configure.zcml', collective.memberapproval, context=configurationContext)
        xmlconfig.file('overrides.zcml', collective.memberapproval, context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.memberapproval:default')

MEMBERAPPROVAL_FIXTURE = MemberApprovalTestSuite()
MEMBERAPPROVAL_INTEGRATION_TESTING = IntegrationTesting(
                                        bases=(MEMBERAPPROVAL_FIXTURE,),
                                        name="MemberApproval:Integration"
                                    )
MEMBERAPPROVAL_FUNCTIONAL_TESTING = FunctionalTesting(
                                        bases=(MEMBERAPPROVAL_FIXTURE,),
                                        name="MemberApproval:Functional"
                                    )
