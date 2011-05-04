from zope.component import getMultiAdapter
from plone.app.users.browser.personalpreferences import UserDataConfiglet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view

class NGBUserDataConfiglet(UserDataConfiglet):
    
    template = ViewPageTemplateFile('account-configlet.pt')
    
    @view.memoize_contextless
    def approval_view(self):
        return getMultiAdapter((self.context, self.request), name=u"user-approval")
        
    def is_approved(self):
        return self.approval_view().is_approved(self.userid)

    def approve_user(self):
        self.approval_view().approve_user(self.userid)
        return self.template()

    def disapprove_user(self):
        self.approval_view().disapprove_user(self.userid)
        return self.template()
