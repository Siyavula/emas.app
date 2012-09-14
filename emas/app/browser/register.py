from zope.formlib import form

from plone.app.users.browser.register import RegistrationForm as BaseRegForm

from emas.app import MessageFactory as _


class RegistrationForm(BaseRegForm):

    @form.action(_(u'label_register', default=u'Register'),
                 validator='validate_registration', name=u'register')
    def action_join(self, action, data):
        self.handle_join_success(data)

        auth = self.context.acl_users.credentials_cookie_auth
        ac_name = getattr(auth, 'name_cookie', '__ac_name')
        ac_password = getattr(auth, 'pw_cookie', '__ac_password')
    
        self.request[ac_name] = self.request.get('form.username')
        self.request[ac_password] = self.request.get('form.password')

        return self.context.unrestrictedTraverse('@@login-from-orderform')()


