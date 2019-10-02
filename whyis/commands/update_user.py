# -*- coding:utf-8 -*-

from flask_script import Command, Option

from flask_security.utils import encrypt_password, verify_password

import flask


class UpdateUser(Command):
    """Update a user in Whyis"""

    def get_options(self):
        return [
            Option('--email', '-e', dest='email',
                   type=str),
            Option('--password', '-p', dest='password',
                   type=str),
            Option('--fn', '-f', dest='fn',
                   type=str),
            Option('--ln', '-l', dest='ln',
                   type=str),
            Option('--username', '-u', dest='identifier', type=str),
            Option('--add-roles', dest="add_roles", type=str),
            Option('--remove-roles', dest="remove_roles", type=str)
        ]

    def run(self, identifier, email, password, fn, ln, add_roles, remove_roles):
        user = flask.current_app.datastore.get_user(identifier)
        print("Modifying user", user.identifier)
        if password is not None:
            verified = verify_password(password, encrypt_password(password))
            if verified:
                user.password = encrypt_password(password)
            else:
                "User password not verified."
        roles = set(user.roles)
        if add_roles is not None:
            for r in add_roles.split(','):
                role = flask.current_app.datastore.find_or_create_role(name=r)
                roles.add(role)
        if remove_roles is not None:
            for r in remove_roles.split(','):
                role = flask.current_app.datastore.find_or_create_role(name=r)
                roles.remove(role)
        user.roles = list(roles)
        if email is not None:
            user.email = email
        if fn is not None:
            user.givenName = fn
        if ln is not None:
            user.familyName = ln
        flask.current_app.datastore.commit()
        print("Updated user: %s" % (user,))
