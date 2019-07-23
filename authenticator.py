from flask import current_app
from flask_login import AnonymousUserMixin, login_user
import datetime

from werkzeug.datastructures import ImmutableList

class InvitedAnonymousUser(AnonymousUserMixin):
    '''A user that has been referred via an external application references but does not have a user account.'''
    def __init__(self):
        self.roles = ImmutableList()

    @staticmethod
    def has_role(*args):
        """Returns `False`"""
        return False

    @staticmethod
    def is_active():
        return True

    @property
    def is_authenticated(self):
        return True


class Authenticator:
    def authenticate(self, request, datastore, config):
        pass

class APIKeyAuthenticator:
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

default_jwt_mapping = {
    'identifier':'sub',
    'email': 'mail',
    'admin': 'isAdmin',
    'givenName' : 'givenName',
    'roles' : 'roles',
    'familyName' : 'sn'
}
        
class JWTAuthenticator:
    def __init__(self,  key, cookie="token", algorithm='HS256', mapping=None):
        if not mapping:
            mapping = default_jwt_mapping
        
        import jwt
        self.jwt = jwt
        self.cookie = cookie
        self.key = key
        self.algorithm = algorithm
        self.mapping = mapping

    def authenticate(self, request, datastore, config):
        token = request.cookies.get(self.cookie)
        if token is not None:
            try:
                payload = self.jwt.decode(token, self.key, algorithms=[self.algorithm])
                user = datastore.get_user(identifier=payload[self.mapping['identifier']])
                if user is None:
                    role_objects = []
                    if self.mapping['roles'] in payload:
                        role_objects = payload[self.mapping['roles']]
                    if self.mapping['admin'] in payload:
                        if payload[self.mapping['admin']] is True:
                            role_objects.append('admin')
                    user = dict(identifier=payload[self.mapping['identifier']],
                                email=payload[self.mapping['email']],
                                givenName=payload[self.mapping['givenName']],
                                familyName=payload[self.mapping['familyName']],
                                confirmed_at = datetime.datetime.utcnow(),
                                roles = role_objects)
                    #user_obj = flask.current_app.datastore.create_user(**user)
                    user_obj = current_app.datastore.create_user(**user)
                else :
                    user_obj = user
                login_user(user_obj)
                return user_obj
            except self.jwt.ExpiredSignatureError:
                return None
        return None
