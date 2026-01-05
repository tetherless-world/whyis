# -*- coding:utf-8 -*-

from flask_script import Command, Option

# Flask-Security-Too renamed encrypt_password to hash_password
try:
    from flask_security.utils import hash_password as encrypt_password
except ImportError:
    # Fallback for older versions
    from flask_security.utils import encrypt_password

import flask

import datetime
import uuid


class CreateUser(Command):
    """Add a user to Whyis"""

    def get_options(self):
        return [
            Option('-e', '--email', dest='email', help='Email address for this user', type=str),
            Option('-p', '--password', dest='password', help='Password for this user', type=str),
            Option('-f', '--fn', dest='fn', help='First name of this user', type=str),
            Option('-l', '--ln', dest='ln', help='Last name of this user', type=str),
            Option('-u', '--username', dest='identifier', help='Username for this user', type=str, required=True),
            Option('--roles', dest="roles", help='Comma-delimited list of role names', type=str)
        ]

    def run(self, email, password, fn, ln, identifier, roles=[]):
        # print('Password verified:', verify_password(password,encrypt_password(password)))
        role_objects = []
        if roles is not None:
            role_objects = [flask.current_app.datastore.find_or_create_role(name=r) for r in roles.split(',')]
        user = dict(id=identifier, email=email,
                    password=encrypt_password(password),
                    givenName=fn, familyName=ln,
                    confirmed_at=datetime.datetime.utcnow(), roles=role_objects,
                    fs_uniquifier=str(uuid.uuid4()))  # Required by Flask-Security-Too 4.0+
        user_obj = flask.current_app.datastore.create_user(**user)
        # print("Created user: %s (%s)" % (user, ''))#', '.join([r.identifier for r in user_obj.roles])))
