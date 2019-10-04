# -*- coding:utf-8 -*-

from flask_script import Command, Option

from flask_security.utils import encrypt_password

import flask

import datetime


class CreateUser(Command):
    """Add a user to Whyis"""

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
            Option('--roles', dest="roles", type=str)
        ]

    def run(self, email, password, fn, ln, identifier, roles=[]):
        # print('Password verified:', verify_password(password,encrypt_password(password)))
        role_objects = []
        if roles is not None:
            role_objects = [flask.current_app.datastore.find_or_create_role(name=r) for r in roles.split(',')]
        user = dict(id=identifier, email=email,
                    password=encrypt_password(password),
                    givenName=fn, familyName=ln,
                    confirmed_at=datetime.datetime.utcnow(), roles=role_objects)
        user_obj = flask.current_app.datastore.create_user(**user)
        # print("Created user: %s (%s)" % (user, ''))#', '.join([r.identifier for r in user_obj.roles])))
