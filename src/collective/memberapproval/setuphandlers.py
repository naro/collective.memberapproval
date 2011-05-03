from pas.plugins.memberapproval.utils import enablePluginInterfaces
from pas.plugins.memberapproval.plugin import MemberapprovalPlugin
from pas.plugins.memberapproval.install import manage_add_memberapproval_plugin

def setupVarious(context):
    if context.readDataFile('collective.memberapproval.txt') is None:
        return 

    portal = context.getSite()
    pas = portal.acl_users
    
    if not pas.objectValues([MemberapprovalPlugin.meta_type,]):
        # add plugin
        manage_add_memberapproval_plugin(portal.acl_users, "source_users_approval")

    # enable the plugin, disable source_users
    enablePluginInterfaces()
