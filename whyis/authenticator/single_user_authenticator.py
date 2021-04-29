from flask_login import login_user

from .authenticator import Authenticator

from flask_login import AnonymousUserMixin

from werkzeug.datastructures import ImmutableList

class SingleUser(AnonymousUserMixin):
    '''A user that has been referred via an external application references but does not have a user account.'''

    def __init__(self):
        self.roles = ImmutableList(['Admin'])

    def has_role(self, *args):
        """Returns `False`"""
        return True

    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

class SingleUserAuthenticator(Authenticator):

    def authenticate(self, request, datastore, config):
        user = SingleUser()
        login_user(user)
        return user
