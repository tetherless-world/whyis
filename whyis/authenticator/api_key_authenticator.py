from flask_login import login_user

from .invited_anonymous_user import InvitedAnonymousUser
from .authenticator import Authenticator


class APIKeyAuthenticator(Authenticator):
    def __init__(self, key, request_arg='API_KEY'):
        self.key = key
        self.request_arg = request_arg

    def authenticate(self, request, datastore, config):
        if self.request_arg in request.args and request.args[self.request_arg] == self.key:
            print('logging in invited user')
            user = InvitedAnonymousUser()
            login_user(user)
            return user
        return None
