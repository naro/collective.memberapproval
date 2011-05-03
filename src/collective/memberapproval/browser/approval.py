from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query

from collective.memberapproval.browser.interfaces import IApprovalView

class ApprovalView(BrowserView):
    implements(IApprovalView)

    @view.memoize_contextless
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx 
            For example: catalog, membership, url
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/tools.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_tools")

    @view.memoize_contextless
    def portal_state(self):
        """ returns 
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/portal.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_portal_state")

    def makeQuery(self, **kw):
        return make_query(**kw)
        
    @property
    @view.memoize
    def plugin(self):
        acl = getToolByName(self.portal_state().portal(), 'acl_users') 
        return acl["source_users_approval"]

    def user_exists(self, userid):
        acl = getToolByName(self.portal_state().portal(), 'acl_users') 
        return userid and (not not acl.getUserById(userid))
        
    def approve_user(self, userid):
        if userid:
            self.plugin.approveUser(userid)

    def unapprove_user(self, userid):
        if userid:
            self.plugin.unapproveUser(userid)
        
    def is_approved(self, userid):
        if userid:
            return self.plugin.userApproved(userid)

    def __call__(self):
        form = self.request.form
        userid = form.get('userid')
        if userid:
            if form.has_key('form.button.approve'):
                self.approve_user(userid)
            elif form.has_key('form.button.unapprove'):
                self.unapprove_user(userid)
        return self.index()
