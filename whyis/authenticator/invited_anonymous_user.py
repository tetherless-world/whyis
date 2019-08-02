from flask_login import AnonymousUserMixin

from werkzeug.datastructures import ImmutableList


class InvitedAnonymousUser(AnonymousUserMixin):
    '''A user that has been referred via an external application references but does not have a user account.'''

    def __init__(self):
        self.roles = ImmutableList()

    def has_role(self, *args):
        """Returns `False`"""
        return False

    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True
