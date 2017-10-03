# -*- coding:utf-8 -*-

from flask_script import Command, Option, prompt_bool

from flask_security.utils import encrypt_password, verify_password, get_hmac

import flask

import os
import datetime
import rdflib
from nanopub import Nanopublication

np = rdflib.Namespace("http://www.nanopub.org/nschema#")

class LoadNanopub(Command):
    def get_options(self):
        return [
            Option('--input', '-i', dest='input_file',
                   type=str),
            Option('--format', '-f', dest='file_format',
                    type=str),
        ]
    
    def run(self, input_file, file_format="trig"):
        '''Add a nanopublication to the knowledge graph.'''
        g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize())
        g1 = g.parse(location=input_file, format=file_format)
        if len(list(g1.subjects(rdflib.RDF.type, np.Nanopublication))) == 0:
            new_np = Nanopublication(store=g1.store)
            new_np.add((new_np.identifier, rdflib.RDF.type, np.Nanopublication))
            new_np.add((new_np.identifier, np.hasAssertion, g1.identifier))
            new_np.add((g1.identifier, rdflib.RDF.type, np.Assertion))
        for npub in flask.current_app.nanopub_manager.prepare(g):
            flask.current_app.nanopub_manager.publish(npub)

class UpdateUser(Command):

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
        """Update a user in the database"""
        user = flask.current_app.datastore.get_user(identifier)
        print "Modifying user", user.resUri
        if password is not None:
            verified = verify_password(password,encrypt_password(password))
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
        print "Updated user: %s" % (user, )

class CreateUser(Command):

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
        """Add a user to your database"""
        print 'Password verified:', verify_password(password,encrypt_password(password))
        role_objects = []
        if roles is not None:
            role_objects = [flask.current_app.datastore.find_or_create_role(name=r) for r in roles.split(',')]
        user = dict(identifier=identifier, email=email,
            password=encrypt_password(password),
            givenName=fn, familyName=ln,
            confirmed_at = datetime.datetime.utcnow(), roles = role_objects)
        user_obj = flask.current_app.datastore.create_user(**user)
        print "Created user: %s (%s)" % (user, ', '.join([r.resUri for r in role_objects]))

class Test(Command):
    """
    Run tests
    """

    verbosity = 2
    failfast = False

    def get_options(self):
        return [
            Option('--verbosity', '-v', dest='verbose',
                    type=int, default=self.verbosity),
            Option('--failfast', dest='failfast',
                    default=self.failfast, action='store_false')
        ]

    def run(self, verbosity, failfast):
        import sys
        import glob
        import unittest

        exists = os.path.exists
        isdir = os.path.isdir
        join = os.path.join

        project_path = os.path.abspath(os.path.dirname('.'))
        sys.path.insert(0, project_path)

        # our special folder for blueprints
        if exists('apps'):
            sys.path.insert(0, join('apps'))

        loader = unittest.TestLoader()
        all_tests = []

        if exists('apps'):
            for path in glob.glob('apps/*'):
                if isdir(path):
                    tests_dir = join(path, 'tests')

                    if exists(join(path, 'tests.py')):
                        all_tests.append(loader.discover(path, 'tests.py'))
                    elif exists(tests_dir):
                        all_tests.append(loader.discover(tests_dir, pattern='test*.py'))

        if exists('tests') and isdir('tests'):
            all_tests.append(loader.discover('tests', pattern='test*.py'))
        elif exists('tests.py'):
            all_tests.append(loader.discover('.', pattern='tests.py'))

        test_suite = unittest.TestSuite(all_tests)
        unittest.TextTestRunner(
            verbosity=verbosity, failfast=failfast).run(test_suite)
