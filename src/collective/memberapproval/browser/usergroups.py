from itertools import chain
from Acquisition import aq_inner
from Products.CMFPlone.utils import normalizeString
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.usergroups import logger

from plone.app.controlpanel.usergroups import \
        UsersOverviewControlPanel as BaseUsersOverviewControlPanel
        
class UsersOverviewControlPanel(BaseUsersOverviewControlPanel):

    def manageUser(self, users=[], resetpassword=[], delete=[]):
        super(UsersOverviewControlPanel, self).manageUser(users, resetpassword, delete)
        acl_users = getToolByName(self.context, 'acl_users')
        form = self.request.form
        all_userids = form.get('is_approved_all', [])
        to_approve = form.get('is_approved', [])
        for userid in all_userids:
            if userid in to_approve:
                acl_users.approveUser(userid)
            else:
                acl_users.disapproveUser(userid)
    
    def doSearch(self, searchString):
        acl = getToolByName(self, 'acl_users')
        rolemakers = acl.plugins.listPlugins(IRolesPlugin)
        
        mtool = getToolByName(self, 'portal_membership')

        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        # First, search for all inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        self.request.set('__ignore_group_roles__', False)
        self.request.set('__ignore_direct_roles__', True)
        inheritance_enabled_users = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
        allInheritedRoles = {}
        for user_info in inheritance_enabled_users:
            userId = user_info['id']
            user = acl.getUserById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warn('Skipped user without principal object: %s' % userId)
                continue
            allAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                allAssignedRoles.extend(rolemaker.getRolesForPrincipal(user))
            allInheritedRoles[userId] = allAssignedRoles

        # We push this in the request such IRoles plugins don't provide
        # the roles from the groups the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_users = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')

        approved_status = self.request.form.get('approved', '')

        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at all (None).
        results = []
        for user_info in explicit_users:
            userId = user_info['id']
            user_approved = acl.userApproved(userId)
            if approved_status=='1':
                if not user_approved:
                    continue
            elif approved_status=='0':
                if user_approved:
                    continue

            user = mtool.getMemberById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warn('Skipped user without principal object: %s' % userId)
                continue
            explicitlyAssignedRoles = []
            for rolemaker_id, rolemaker in rolemakers:
                explicitlyAssignedRoles.extend(rolemaker.getRolesForPrincipal(user))

            roleList = {}
            for role in self.portal_roles:
                canAssign = user.canAssignRole(role)
                if role == 'Manager' and not self.is_zope_manager:
                    canAssign = False
                roleList[role]={'canAssign': canAssign,
                                'explicit': role in explicitlyAssignedRoles,
                                'inherited': role in allInheritedRoles[userId]}

            canDelete = user.canDelete()
            canPasswordSet = user.canPasswordSet()
            if roleList['Manager']['explicit'] or roleList['Manager']['inherited']:
                if not self.is_zope_manager:
                    canDelete = False
                    canPasswordSet = False

            user_info['roles'] = roleList
            user_info['fullname'] = user.getProperty('fullname', '')
            user_info['email'] = user.getProperty('email', '')
            user_info['can_delete'] = canDelete
            user_info['can_set_email'] = user.canWriteProperty('email')
            user_info['can_set_password'] = canPasswordSet
            user_info['is_approved'] = user_approved
            results.append(user_info)

        # Sort the users by fullname
        results.sort(key=lambda x: x is not None and x['fullname'] is not None and normalizeString(x['fullname']) or '')

        # Reset the request variable, just in case.
        self.request.set('__ignore_group_roles__', False)
        return results
