from zope.formlib import form

from plone.app.users.browser.register import RegistrationForm as BaseRegForm

from emas.app import MessageFactory as _


class RegistrationForm(BaseRegForm):

    @form.action(_(u'label_register', default=u'Register'),
                 validator='validate_registration', name=u'register')
    def action_join(self, action, data):
        self.handle_join_success(data)
        came_from = '%s/order' %self.context.absolute_url()
        self.request['came_from'] = came_from
        return self.context.unrestrictedTraverse('registered')()
