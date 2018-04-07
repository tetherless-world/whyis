# -*- coding:utf-8 -*-

from flask_script import Command, Option, prompt_bool

from flask_security.utils import encrypt_password, verify_password, get_hmac

import flask


from base64 import b64encode
import os
import datetime
import rdflib
from nanopub import Nanopublication
from cookiecutter.main import cookiecutter
import tempfile

np = rdflib.Namespace("http://www.nanopub.org/nschema#")

def rando():
    return b64encode(os.urandom(24)).decode('utf-8')

    
class Configure(Command):
    '''Create a Whyis configuration and customization directory.'''
    def get_options(self):
        return [
        ]
    
    def run(self, extension_directory=None, extension_name=None):
        # Create project from the cookiecutter-pypackage/ template
        extra_context = { 'SECRET_KEY':rando(), 'SECURITY_PASSWORD_SALT': rando() }
        cookiecutter('config-template/', extra_context=extra_context)

class LoadNanopub(Command):
    '''Add a nanopublication to the knowledge graph.'''
    def get_options(self):
        return [
            Option('--input', '-i', dest='input_file',
                   type=str),
            Option('--format', '-f', dest='file_format',
                    type=str),
            Option('--revises', '-r', dest='was_revision_of',
                    type=str),
        ]
    
    def run(self, input_file, file_format="trig", was_revision_of=None):
        if was_revision_of is not None:
            wasRevisionOf = set(flask.current_app.db.objects(predicate=np.hasAssertion,
                                                               subject=rdflib.URIRef(was_revision_of)))
            if len(wasRevisionOf) == 0:
                print "Could not find active nanopublication to revise:", was_revision_of
                return
            was_revision_of = wasRevisionOf
        g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize(), store="Sleepycat")
        graph_tempdir = tempfile.mkdtemp()
        g.store.open(graph_tempdir, True)
        #g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize())

        g1 = g.parse(location=input_file, format=file_format, publicID=flask.current_app.NS.local)
        if len(list(g.subjects(rdflib.RDF.type, np.Nanopublication))) == 0:
            print "Could not find existing nanopublications.", len(g1), len(g)
            new_np = Nanopublication(store=g1.store)
            new_np.add((new_np.identifier, rdflib.RDF.type, np.Nanopublication))
            new_np.add((new_np.identifier, np.hasAssertion, g1.identifier))
            new_np.add((g1.identifier, rdflib.RDF.type, np.Assertion))

        nanopub_prepare_graph = rdflib.ConjunctiveGraph(store="Sleepycat")
        nanopub_prepare_graph_tempdir = tempfile.mkdtemp()
        nanopub_prepare_graph.store.open(nanopub_prepare_graph_tempdir, True)
        nanopubs = []
        for npub in flask.current_app.nanopub_manager.prepare(g, store=nanopub_prepare_graph.store):
            if was_revision_of is not None:
                for r in was_revision_of:
                    print "Marking as revision of", r
                    npub.pubinfo.add((npub.assertion.identifier, flask.current_app.NS.prov.wasRevisionOf, r))
            print 'Prepared', npub.identifier
            nanopubs.append(npub)
        flask.current_app.nanopub_manager.publish(*nanopubs)
        print "Published", npub.identifier

class RetireNanopub(Command):
    '''Retire a nanopublication from the knowledge graph.'''
    def get_options(self):
        return [
            Option('--nanopub_uri', '-n', dest='nanopub_uri',
                   type=str),
        ]
    
    def run(self, nanopub_uri):
        flask.current_app.nanopub_manager.retire(nanopub_uri)
        
class TestAgent(Command):
    '''Add a nanopublication to the knowledge graph.'''
    def get_options(self):
        return [
            Option('--agent', '-a', dest='agent_path',
                   type=str),
            Option('--dry-run', '-d', action="store_true", dest='dry_run'),
        ]
    
    def run(self, agent_path, dry_run=False):
        app = flask.current_app
        from pydoc import locate
        agent_class = locate(agent_path)
        agent = agent_class()
        agent.dry_run = dry_run
        if agent.dry_run:
            print "Dry run, not storing agent output."
        agent.app = app
        print agent.get_query()
        results = []
        if agent.query_predicate == app.NS.whyis.globalChangeQuery:
            results.extend(agent.process_graph(app.db))
        else:
            for resource in agent.getInstances(app.db):
                for np_uri, in app.db.query('''select ?np where {
    graph ?assertion { ?e ?p ?o.}
    ?np a np:Nanopublication;
        np:hasAssertion ?assertion.
}''', initBindings={'e': resource.identifier}, initNs=app.NS.prefixes):
                    np = app.nanopub_manager.get(np_uri)
                    results.extend(agent.process_graph(np))
        for np in results:
            print np.serialize(format="trig")
            
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
