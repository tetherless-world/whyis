# -*- coding:utf-8 -*-
import importlib
import os
import sys
from datetime import datetime
from functools import lru_cache
from re import finditer
from urllib.parse import urlencode

import collections
import json

import jinja2
import pytz
import rdflib
import sadi
import sadi.mimeparse
from celery import Celery
from celery_once import QueueOnce
from celery.schedules import crontab
from depot.manager import DepotManager
from depot.middleware import FileServeApp
from depot.io.utils import FileIntent
from flask import render_template, g, redirect, url_for, request, flash, send_from_directory, abort
from flask_security import Security
from flask_security.core import current_user
from flask_security.forms import RegisterForm
from rdflib import Literal, Graph, Namespace, URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.query import Processor, Result, UpdateProcessor
from slugify import slugify
from werkzeug.exceptions import Unauthorized
from werkzeug.utils import secure_filename
from wtforms import StringField, validators

from whyis import database
from whyis import filters
from whyis import search
from whyis import fuseki
from whyis import plugin as plugin
from whyis.blueprint.entity import entity_blueprint
from whyis.blueprint.nanopub import nanopub_blueprint
from whyis.blueprint.tableview import tableview_blueprint
from whyis.blueprint.sparql import sparql_blueprint
from whyis.data_extensions import DATA_EXTENSIONS
from whyis.data_formats import DATA_FORMATS
from whyis.datastore import WhyisUserDatastore
from whyis.decorator import conditional_login_required
from whyis.empty import Empty
from whyis.html_mime_types import HTML_MIME_TYPES
from whyis.namespace import NS
from whyis.nanopub import NanopublicationManager
from whyis.authenticator import SingleUserAuthenticator
# from flask_login.config import EXEMPT_METHODS
from pkg_resources import resource_filename

rdflib.plugin.register('sparql', Result,
        'rdflib.plugins.sparql.processor', 'SPARQLResult')
rdflib.plugin.register('sparql', Processor,
        'rdflib.plugins.sparql.processor', 'SPARQLProcessor')
rdflib.plugin.register('sparql', UpdateProcessor,
        'rdflib.plugins.sparql.processor', 'SPARQLUpdateProcessor')

# apps is a special folder where you can place your blueprints
PROJECT_PATH = resource_filename(__name__,"")

# we create some comparison keys:
# increase probability that the rule will be near or at the top
# top_compare_key = False, -100, [(-2, 0)]
# increase probability that the rule will be near or at the bottom
bottom_compare_key = True, 100, [(2, 0)]


# Setup Flask-Security
class ExtendedRegisterForm(RegisterForm):
    id = StringField('Identifier', [validators.InputRequired()])
    givenName = StringField('Given Name', [validators.InputRequired()])
    familyName = StringField('Family Name', [validators.InputRequired()])

# def to_json(result):
#     return json.dumps([ {key: value.value if isinstance(value, Literal) else value for key, value in list(x.items())} for x in result.bindings])


class App(Empty):

    managed = False
    listeners = collections.defaultdict(list)

    def resolve(self, term, type=None, context=None, label=False):
        for resolver in self.listeners['on_resolve']:
            results = resolver.on_resolve(term, type, context, label)
            if len(results) > 0:
                return results
        return []

    def configure_extensions(self):

        Empty.configure_extensions(self)

        if self.config.get('EMBEDDED_CELERY',False):
            # self.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
            # self.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
            from redislite import Redis
            self.rdb = Redis(os.path.join('run','redis.db'))
            print("Starting redis...")
            self.config['CELERY_BROKER_URL'] = 'redis+socket://%s' % (self.rdb.socket_file, )
            self.config['CELERY_RESULT_BACKEND'] = self.config['CELERY_BROKER_URL']

        self.celery = Celery(self.name, broker=self.config['CELERY_BROKER_URL'], beat=True)
        self.celery.conf.update(self.config)
        self.celery.conf.ONCE = {
            'backend': 'celery_once.backends.Redis',
            'settings': {
                'url': self.config['CELERY_BROKER_URL'],
                'default_timeout': 60 * 60 * 24
            }
        }
        class ContextTask(self.celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        self.celery.Task = ContextTask

        # Make QueueOnce app context aware.
        class ContextQueueOnce(QueueOnce):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super(ContextQueueOnce, self).__call__(*args, **kwargs)

        # Attach to celery object for easy access.
        self.celery.QueueOnce = ContextQueueOnce

        app = self

        if 'root_path' in self.config:
            self.root_path = self.config['root_path']

        if 'WHYIS_TEMPLATE_DIR' in self.config and app.config['WHYIS_TEMPLATE_DIR'] is not None:
            my_loader = jinja2.ChoiceLoader(
                [jinja2.FileSystemLoader(p) for p in self.config['WHYIS_TEMPLATE_DIR']]
                + [app.jinja_loader]
            )
            app.jinja_loader = my_loader

        @self.celery.task(base=QueueOnce, once={'graceful': True})
        def process_resource(service_name, entity, taskid=None):
            with app.app_context():
                service = self.config['INFERENCERS'][service_name]
                service.app = self
                instance = app.db.resource(entity)
                service.process_instance(instance, app.db)

        @self.celery.task
        def process_nanopub(nanopub_uri, service_name, entity, taskid=None):
            with app.app_context():
                service = self.config['INFERENCERS'][service_name]
                if app.nanopub_manager.is_current(nanopub_uri):
                    print("Running task", service_name, 'on', nanopub_uri)
                    service.app = app
                    nanopub = app.nanopub_manager.get(nanopub_uri)
                    instance = nanopub.assertion.resource(entity)
                    service.process_instance(instance, nanopub)
                else:
                    print("Skipping retired nanopub", nanopub_uri)

        def setup_periodic_task(task):
            @self.celery.task
            def find_instances():
                print("Triggered task", task['name'])
                for x in task['service'].getInstances(app.db):
                    task['do'](x.identifier)

            @self.celery.task
            def do_task(uri):
                print("Running task", task['name'], 'on', uri)
                resource = app.db.resource(uri)

                # result never used
                task['service'].process_instance(resource, app.db)

            task['service'].app = app
            task['find_instances'] = find_instances
            task['do'] = do_task

            return task

        app.inference_tasks = []
        if 'INFERENCE_TASKS' in self.config:
            app.inference_tasks = [setup_periodic_task(task) for task in self.config['INFERENCE_TASKS']]

        for name, task in list(self.config['INFERENCERS'].items()):
            print("Adding app to",task)
            task.app = app

        for task in app.inference_tasks:
            if 'schedule' in task:
                #print "Scheduling task", task['name'], task['schedule']
                self.celery.add_periodic_task(
                    crontab(**task['schedule']),
                    task['find_instances'].s(),
                    name=task['name']
                )
            else:
                task['find_instances'].delay()

        @self.celery.task()
        def update(nanopub_uri):
            '''gets called whenever there is a change in the knowledge graph.
            Performs a breadth-first knowledge expansion of the current change.'''
            print("Updating on", nanopub_uri)
            #if not app.nanopub_manager.is_current(nanopub_uri):
            #    print("Skipping retired nanopub", nanopub_uri)
            #    return
            nanopub = app.nanopub_manager.get(nanopub_uri)
            nanopub_graph = ConjunctiveGraph(nanopub.store)
            if 'INFERENCERS' in self.config:
                for name, service in list(self.config['INFERENCERS'].items()):
                    service.app = self
                    if service.query_predicate == self.NS.whyis.updateChangeQuery:
                        for instance in service.getInstances(nanopub_graph):
                            print("Running agent %s on %s in %s" % (service, instance.identifier, nanopub_uri))
                            process_nanopub.apply_async(kwargs={
                                'nanopub_uri': nanopub_uri,
                                'service_name':name,
                                'entity':instance.identifier
                            }, priority=1 )
                for name, service in list(self.config['INFERENCERS'].items()):
                    service.app = self
                    if service.query_predicate == self.NS.whyis.globalChangeQuery:
                        for instance in service.getInstances(self.db):
                            process_resource.apply_async(kwargs={
                                'service_name':name,
                                'entity':instance.identifier
                            }, priority=5)

        def run_update(nanopub_uri):
            print('Adding to agent queue: %s' % nanopub_uri)
            update.apply_async(args=[nanopub_uri],priority=9)
        self.nanopub_update_listener = run_update

        app = self
        @self.celery.task(base=self.celery.QueueOnce,
                          once={'graceful': True},
                          retry_backoff=True,
                          retry_jitter=True,
                          autoretry_for=(Exception,),
                          max_retries=4,
                          bind=True)
        def run_importer(self, entity_name):
            entity_name = URIRef(entity_name)
            print('importing', entity_name)
            importer = app.find_importer(entity_name)
            if importer is None:
                return
            importer.app = app
            modified = importer.last_modified(entity_name, app.db, app.nanopub_manager)
            updated = importer.modified(entity_name)
            if updated is None:
                updated = datetime.now(pytz.utc)
            if modified is None or (updated - modified).total_seconds() > importer.min_modified:
                importer.load(entity_name, app.db, app.nanopub_manager)

        self.run_importer = run_importer

        self.template_imports = {}
        if 'template_imports' in self.config:
            for name, imp in list(self.config['template_imports'].items()):
                try:
                    m = importlib.import_module(imp)
                    self.template_imports[name] = m
                except Exception:
                    print("Error importing module %s into template variable %s." % (imp, name))
                    raise

        self.nanopub_manager = NanopublicationManager(self.db.store,
                                                      Namespace('%s/pub/'%(self.config['LOD_PREFIX'])),
                                                      self,
                                                      update_listener=self.nanopub_update_listener)

        if 'CACHE_TYPE' in self.config:
            from flask_caching import Cache
            self.cache = Cache(self)
        else:
            self.cache = None

    _file_depot = None
    @property
    def file_depot(self):
        print(self.config['FILE_ARCHIVE'])
        #if self._file_depot is None:
        if DepotManager.get('files') is None:
            print("constructing new depot")
            DepotManager.configure('files', self.config['FILE_ARCHIVE'])
            #self._file_depot =
        return DepotManager.get('files')
        #return self._file_depot

    _nanopub_depot = None
    @property
    def nanopub_depot(self):
        if self._nanopub_depot is None and 'NANOPUB_ARCHIVE' in self.config:
            if DepotManager.get('nanopublications') is None:
                DepotManager.configure('nanopublications', self.config['NANOPUB_ARCHIVE'])
            self._nanopub_depot = DepotManager.get('nanopublications')
        return self._nanopub_depot

    datastore = None
    fuseki_server = None

    @nanopub_depot.setter
    def nanopub_depot(self, value):
        self._nanopub_depot = value

    def add_listener(self, listener):
        for signal in listener.signals:
            self.listeners[signal].append(listener)

    def configure_database(self):
        """
        Database configuration should be set here
        """
        self.NS = NS
        self.NS.local = rdflib.Namespace(self.config['LOD_PREFIX']+'/')

        if self.config.get('EMBEDDED_FUSEKI', False) and self.fuseki_server is None:
            self.fuseki_port = fuseki.find_free_port()
            print("Starting Fuseki on port",self.fuseki_port)
            self.fuseki_server = fuseki.FusekiServer(port=self.fuseki_port)

            self.config['FUSEKI_PORT'] = self.fuseki_port
            knowledge_endpoint = self.fuseki_server.get_dataset('/knowledge')
            print("Knowledge Endpoint:", knowledge_endpoint)
            self.config['KNOWLEDGE_ENDPOINT'] = knowledge_endpoint
            admin_endpoint = self.fuseki_server.get_dataset('/admin')
            self.config['ADMIN_ENDPOINT'] = admin_endpoint
            print("Admin Endpoint:", admin_endpoint)

        self.admin_db = database.engine_from_config(self.config.get_namespace('ADMIN'))
        self.db = database.engine_from_config(self.config.get_namespace("KNOWLEDGE"))
        self.db.app = self

        self.databases = {}
        self.databases['admin'] = self.admin_db
        self.databases['knowledge'] = self.db

        for db in self.config.get('DATABASES',[]):
            db_instance = database.engine_from_config(self.config.get_namespace(db))
            self.databases[db_instance.name] = db_instance
            if isinstance(db_instance, plugin.Listener):
                self.add_listener(db_instance)

        self.vocab = ConjunctiveGraph()
        #print URIRef(self.config['vocab_file'])
        default_vocab = Graph(store=self.vocab.store)
        default_vocab.parse(source=os.path.abspath(os.path.join(os.path.dirname(__file__), "default_vocab.ttl")), format="turtle", publicID=str(self.NS.local))
        print("Vocab size:", len(self.vocab))
        for p in self.plugins:
            p.vocab(self.vocab.store)
            print("Vocab size:", len(self.vocab))
        if 'VOCAB_FILE' in self.config and os.path.exists(self.config['VOCAB_FILE']):
            print(self.config['VOCAB_FILE'])
            custom_vocab = Graph(store=self.vocab.store)
            custom_vocab.parse(self.config['VOCAB_FILE'], format="turtle", publicID=str(self.NS.local))
            print("Vocab size:", len(self.vocab))
        else:
            print("Not loading custom view mappings.")

        if self.datastore is None:
            self.datastore = WhyisUserDatastore(self.admin_db, {}, self.config['LOD_PREFIX'])
            self.security = Security(self, self.datastore,
                                     register_form=ExtendedRegisterForm)
        else:
            self.datastore.db = self.admin_db

    def __weighted_route(self, *args, **kwargs):
        """
        Override the match_compare_key function of the Rule created by invoking Flask.route.
        This can only be done on the app, not in a blueprint, because blueprints lazily add Rule's when they are registered on an app.
        """

        def decorator(view_func):
            compare_key = kwargs.pop('compare_key', None)
            # register view_func with route
            self.route(*args, **kwargs)(view_func)

            if compare_key is not None:
                rule = self.url_map._rules[-1]
                rule.match_compare_key = lambda: compare_key

            return view_func
        return decorator

    def map_entity(self, name):
        for importer in self.config['NAMESPACES']:
            if importer.matches(name):
                new_name = importer.map(name)
                #print 'Found mapped URI', new_name
                return new_name, importer
        return None, None

    def find_importer(self, name):
        for importer in self.config['NAMESPACES']:
            if importer.resource_matches(name):
                return importer
        return None


    class Entity (rdflib.resource.Resource):
        _this = None

        def this(self):
            if self._this is None:
                self._this = self._graph.app.get_entity(self.identifier)
            return self._this

        _description = None

        def description(self):
            if self._description is None:
#                try:
                result = Graph()
#                try:
                for quad in self._graph.query('''describe ?e
# construct {
#     ?e ?p ?o.
#     ?o rdfs:label ?label.
#     ?o skos:prefLabel ?prefLabel.
#     ?o dc:title ?title.
#     ?o foaf:name ?name.
#     ?o ?pattr ?oattr.
#     ?oattr rdfs:label ?oattrlabel
# } where {
#     graph ?g {
#       ?e ?p ?o.
#     }
#     ?g a np:Assertion.
#     optional {
#       ?e sio:hasAttribute|sio:hasPart ?o.
#       ?o ?pattr ?oattr.
#       optional {
#         ?oattr rdfs:label ?oattrlabel.
#       }
#     }
#     optional {
#       ?o rdfs:label ?label.
#     }
#     optional {
#       ?o skos:prefLabel ?prefLabel.
#     }
#     optional {
#       ?o dc:title ?title.
#     }
#     optional {
#       ?o foaf:name ?name.
#     }
# }
''', initNs=NS.prefixes, initBindings={'e':self.identifier}):
                    if len(quad) == 3:
                        s,p,o = quad
                    else:
                        # Last term is never used
                        s,p,o,_ = quad
                    result.add((s,p,o))
#                except:
#                    pass
                self._description = result.resource(self.identifier)
#                except Exception as e:
#                    print str(e), self.identifier
#                    raise e
            return self._description

    def get_resource(self, entity, async_=True, retrieve=True):
        if retrieve:
            mapped_name, importer = self.map_entity(entity)

            if mapped_name is not None:
                entity = mapped_name

            if importer is None:
                importer = self.find_importer(entity)

            if importer is not None:
                modified = importer.last_modified(entity, self.db, self.nanopub_manager)
                if modified is None or async_ is False:
                    self.run_importer(entity)
                elif not importer.import_once:
                    self.run_importer.delay(entity)
        return self.Entity(self.db, entity)

    def configure_template_filters(self):
        filters.configure(self)
        if 'filters' in self.config:
            for name, fn in self.config['filters'].items():
                self.template_filter(name)(fn)


    def add_file(self, f, entity, nanopub):
        entity = rdflib.URIRef(entity)
        old_nanopubs = []
        for np_uri, np_assertion, in self.db.query('''select distinct ?np ?assertion where {
    hint:Query hint:optimizer "Runtime" .
    graph ?assertion {?e whyis:hasFileID ?fileid}
    ?np np:hasAssertion ?assertion.
}''', initNs=NS.prefixes, initBindings=dict(e=rdflib.URIRef(entity))):
            if not self._can_edit(np_uri):
                raise Unauthorized()
            old_nanopubs.append((np_uri, np_assertion))
        fileintent = FileIntent(f.stream, f.filename, f.mimetype)
        fileid = self.file_depot.create(fileintent)
        self.file_depot.get(fileid)
        print(self.file_depot)
        print("added",entity,"to depot as",fileid)
        nanopub.add((nanopub.identifier, NS.sio.isAbout, entity))
        nanopub.assertion.add((entity, NS.whyis.hasFileID, Literal(fileid)))
        if current_user._get_current_object() is not None and hasattr(current_user, 'identifier'):
            nanopub.assertion.add((entity, NS.dc.contributor, current_user.identifier))
        nanopub.assertion.add((entity, NS.dc.created, Literal(datetime.utcnow())))
        nanopub.assertion.add((entity, NS.ov.hasContentType, Literal(f.mimetype)))
        nanopub.assertion.add((entity, NS.RDF.type, NS.mediaTypes[f.mimetype]))
        nanopub.assertion.add((NS.mediaTypes[f.mimetype], NS.RDF.type, NS.dc.FileFormat))
        nanopub.assertion.add((entity, NS.RDF.type, NS.mediaTypes[f.mimetype.split('/')[0]]))
        nanopub.assertion.add((NS.mediaTypes[f.mimetype.split('/')[0]], NS.RDF.type, NS.dc.FileFormat))
        nanopub.assertion.add((entity, NS.RDF.type, NS.pv.File))

        if current_user._get_current_object() is not None and hasattr(current_user, 'identifier'):
            nanopub.pubinfo.add((nanopub.assertion.identifier, NS.dc.contributor, current_user.identifier))
        nanopub.pubinfo.add((nanopub.assertion.identifier, NS.dc.created, Literal(datetime.utcnow())))

        return old_nanopubs

    def delete_file(self, entity):
        for np_uri, in self.db.query('''select distinct ?np where {
    hint:Query hint:optimizer "Runtime" .
    graph ?np_assertion {?e whyis:hasFileID ?fileid}
    ?np np:hasAssertion ?np_assertion.
}''', initNs=NS.prefixes, initBindings=dict(e=entity)):
            if not self._can_edit(np_uri):
                raise Unauthorized()
            self.nanopub_manager.retire(np_uri)


    def add_files(self, uri, files, upload_type=NS.pv.File):
        nanopub = self.nanopub_manager.new()

        added_files = False

        old_nanopubs = []
        nanopub.assertion.add((uri, self.NS.RDF.type, upload_type))
        if upload_type == URIRef("http://purl.org/dc/dcmitype/Collection"):
            for f in files:
                filename = secure_filename(f.filename)
                if filename != '':
                    file_uri = URIRef(uri+"/"+filename)
                    old_nanopubs.extend(self.add_file(f, file_uri, nanopub))
                    nanopub.assertion.add((uri, NS.dc.hasPart, file_uri))
                    added_files = True
        elif upload_type == NS.dcat.Dataset:
            for f in files:
                filename = secure_filename(f.filename)
                if filename != '':
                    file_uri = URIRef(uri+"/"+filename)
                    old_nanopubs.extend(self.add_file(f, file_uri, nanopub))
                    nanopub.assertion.add((uri, NS.dcat.distribution, file_uri))
                    nanopub.assertion.add((file_uri, NS.RDF.type, NS.dcat.Distribution))
                    nanopub.assertion.add((file_uri, NS.dcat.downloadURL, file_uri))
                    added_files = True
        else:
            for f in files:
                if f.filename != '':
                    old_nanopubs.extend(self.add_file(f, uri, nanopub))
                    nanopub.assertion.add((uri, NS.RDF.type, NS.pv.File))
                    added_files = True
                    break

        if added_files:
            for old_np, old_np_assertion in old_nanopubs:
                nanopub.pubinfo.add((nanopub.assertion.identifier, NS.prov.wasRevisionOf, old_np_assertion))
                self.nanopub_manager.retire(old_np)

            for n in self.nanopub_manager.prepare(nanopub):
                self.nanopub_manager.publish(n)

    def _can_edit(self, uri):
        if self.managed:
            return True
        if current_user._get_current_object() is None:
            # This isn't null even when not authenticated, unless we are an autonomic agent.
            return True
        if not hasattr(current_user, 'identifier'): # This is an anonymous user.
            return False
        if current_user.has_role('Publisher') or current_user.has_role('Editor')  or current_user.has_role('Admin'):
            return True
        if self.db.query('''ask {
    ?nanopub np:hasAssertion ?assertion; np:hasPublicationInfo ?info.
    graph ?info { ?assertion dc:contributor ?user. }
}''', initBindings=dict(nanopub=uri, user=current_user.identifier), initNs=dict(np=self.NS.np, dc=self.NS.dc)):
            return True
        return False

    def configure_views(self):

        def sort_by(resources, property):
            return sorted(resources, key=lambda x: x.value(property))

        def camel_case_split(identifier):
            matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
            return [m.group(0) for m in matches]

        label_properties = [
            self.NS.skos.prefLabel,
            self.NS.RDFS.label,
            URIRef('http://purl.org/dc/terms/title'),
            self.NS.schema.name,
            self.NS.foaf.name,
            self.NS.skos.notation]

        @lru_cache(maxsize=1000)
        def get_remote_label(uri):
            for db in [self.db, self.admin_db]:
                g = Graph()
                try:
                    db.nsBindings = {}
                    g += db.query('''select ?s ?p ?o where {
                        hint:Query hint:optimizer "Runtime" .

                         ?s ?p ?o.}''',
                                  initNs=self.NS.prefixes, initBindings=dict(s=uri))
                    db.nsBindings = {}
                except:
                    pass
                resource_entity = g.resource(uri)
                if len(resource_entity.graph) == 0:
                    continue
                for property in label_properties:
                    labels = self.lang_filter(resource_entity[property])
                    if len(labels) > 0:
                        return labels[0]

                if len(labels) == 0:
                    name = [x.value for x in [resource_entity.value(self.NS.foaf.givenName),
                                              resource_entity.value(self.NS.foaf.familyName)] if x is not None]
                    if len(labels) == 0:
                        name = [x.value for x in [resource_entity.value(self.NS.schema.givenName),
                                                  resource_entity.value(self.NS.schema.familyName)] if x is not None]
                        if len(name) > 0:
                            label = ' '.join(name)
                            return label
            try:
                label = self.db.qname(uri).split(":")[1].replace("_"," ")
                return ' '.join(camel_case_split(label)).title()
            except Exception as e:
                print(str(e), uri)
                return str(uri)

        def get_label(resource):
            for property in label_properties:
                labels = self.lang_filter(resource.graph.objects(resource.identifier, property))
                if len(labels) > 0:
                    return labels[0]
            return get_remote_label(resource.identifier)

        self.get_label = get_label

        def initialize_g():
            if not hasattr(g, "initialized"):
                g.initialized = True
                g.ns = self.NS
                g.get_summary = get_summary
                g.get_label = get_label
                g.labelize = self.labelize
                g.get_resource = self.get_resource
                g.get_entity = self.get_entity
                g.rdflib = rdflib
                g.isinstance = isinstance
                g.current_user = current_user
                g.slugify = slugify
                g.db = self.db


        self.initialize_g = initialize_g

        if not self.config.get("MULTIUSER", True):
            self.config['AUTHENTICATORS'] = [SingleUserAuthenticator()]

        @self.before_request
        def load_forms():

            if 'AUTHENTICATORS' in self.config:
                for authenticator in self.config['AUTHENTICATORS']:
                    user = authenticator.authenticate(request, self.datastore, self.config)
                    if user is not None:
                    #    login_user(user)
                        break
            initialize_g()

        @self.login_manager.user_loader
        def load_user(user_id):
            if user_id != None:
                #try:
                user = self.datastore.find_user(id=user_id)
                return user
                #except:
                #    return None
            else:
                return None


        # def get_graphs(graphs):
        #     query = '''select ?s ?p ?o ?g where {
        #         hint:Query hint:optimizer "Runtime" .
        #
        #         graph ?g {?s ?p ?o}
        #         } values ?g { %s }'''
        #     query = query % ' '.join([graph.n3() for graph in graphs])
        #     #print query
        #     quads = self.db.store.query(query, initNs=self.NS.prefixes)
        #     result = rdflib.Dataset()
        #     result.addN(quads)
        #     return result

#         def explain(graph):
#             values = ')\n  ('.join([' '.join([x.n3() for x in triple]) for triple in graph.triples((None,None,None))])
#             values = 'VALUES (?s ?p ?o)\n{\n('+ values + ')\n}'
#
#             try:
#                 nanopubs = self.db.query('''select distinct ?np where {
#     hint:Query hint:optimizer "Runtime" .
#     ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
#         np:hasPublicationInfo ?pubinfo;
#         np:hasAssertion ?assertion;
#     graph ?assertion { ?s ?p ?o.}
# }''' + values, initNs=self.NS.prefixes)
#                 result = ConjunctiveGraph()
#                 for nanopub_uri, in nanopubs:
#                     self.nanopub_manager.get(nanopub_uri, result)
#             except Exception as e:
#                 print(str(e), entity)
#                 raise e
#             return result.resource(entity)

        def get_entity_sparql(entity):
            try:
                statements = self.db.query('''select distinct ?s ?p ?o ?g where {
    hint:Query hint:optimizer "Runtime" .
            ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
                np:hasPublicationInfo ?pubinfo;
                np:hasAssertion ?assertion;

            {graph ?np { ?np sio:isAbout|sio:SIO_000332 ?e.}}
            UNION
            {graph ?assertion { ?e ?p ?o.}}
            graph ?g { ?s ?p ?o }
        }''',initBindings={'e':entity}, initNs=self.NS.prefixes)
                result = ConjunctiveGraph()
                result.addN(statements)
            except Exception as e:
                print(str(e), entity)
                raise e
            #print result.serialize(format="trig")
            return result.resource(entity)


#         def get_entity_disk(entity):
#             try:
#                 nanopubs = self.db.query('''select distinct ?np where {
#     hint:Query hint:optimizer "Runtime" .
#             ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
#                 np:hasPublicationInfo ?pubinfo;
#                 np:hasAssertion ?assertion;
#
#             {graph ?np { ?np sio:isAbout ?e.}}
#             UNION
#             {graph ?assertion { ?e ?p ?o.}}
#         }''',initBindings={'e':entity}, initNs=self.NS.prefixes)
#                 result = ConjunctiveGraph()
#                 for nanopub_uri, in nanopubs:
#                     self.nanopub_manager.get(nanopub_uri, result)
# #                result.addN(nanopubs)
#             except Exception as e:
#                 print(str(e), entity)
#                 raise e
#             #print result.serialize(format="trig")
#             return result.resource(entity)

        get_entity = get_entity_sparql

        self.get_entity = get_entity

        def get_summary(resource):
            summary_properties = [
                self.NS.skos.definition,
                self.NS.schema.description,
                self.NS.dc.abstract,
                self.NS.dc.description,
                self.NS.dc.summary,
                self.NS.RDFS.comment,
                self.NS.dcelements.description,
                URIRef("http://purl.obolibrary.org/obo/IAO_0000115"),
                self.NS.prov.value,
                self.NS.sio.hasValue
            ]
            if 'summary_properties' in self.config:
                summary_properties.extend(self.config['summary_properties'])
            for property in summary_properties:
                terms = self.lang_filter(resource[property])
                for term in terms:
                    yield (property, term)

        self.get_summary = get_summary

        if 'WHYIS_CDN_DIR' in self.config and self.config['WHYIS_CDN_DIR'] is not None:
            @self.route('/cdn/<path:filename>')
            def cdn(filename):
                return send_from_directory(self.config['WHYIS_CDN_DIR'], filename)

        @self.route('/favicon.ico')
        def favicon():
            return redirect("/static/images/favicon.ico")

        def render_view(resource, view=None, args=None, use_cache=True):
            self.initialize_g()
            if view is None and 'view' in request.args:
                view = request.args['view']

            if view is None:
                view = 'view'

            if use_cache and self.cache is not None:
                key = str((str(resource.identifier),view))
                result = self.cache.get(key)
                if result is not None:
                    r, headers = result
                    return r, 200, headers
            template_args = dict()
            template_args.update(self.template_imports)
            template_args.update(dict(
                ns=self.NS,
                this=resource, g=g,
                current_user=current_user,
                isinstance=isinstance,
                args=request.args if args is None else args,
                url_for=url_for,
                app=self,
                view=view,
                get_entity=get_entity,
                get_summary=get_summary,
                lang_filter=self.lang_filter,
                search = search,
                rdflib=rdflib,
                config=self.config,
                hasattr=hasattr,
                set=set))

            types = []
            if 'as' in request.args:
                types = [URIRef(request.args['as']), 0]

            types.extend((x, 1) for x in self.vocab[resource.identifier : NS.RDF.type])
            if len(types) == 0: # KG types cannot override vocab types. This should keep views stable where critical.
                types.extend([(x.identifier, 1) for x in resource[NS.RDF.type]  if isinstance(x.identifier, rdflib.URIRef)])
            #if len(types) == 0:
            types.append([self.NS.RDFS.Resource, 100])
            print(types)
            type_string = ' '.join(["(%s %d '%s')" % (x.n3(), i, view) for x, i in types])
            view_query = '''select ?id ?view (count(?mid)+?priority as ?rank) ?class ?c ?content_type where {
    values (?c ?priority ?id) { %s }
    ?c rdfs:subClassOf* ?mid.
    ?mid rdfs:subClassOf* ?class.
    ?class ?viewProperty ?view.
    ?viewProperty rdfs:subPropertyOf* whyis:hasView.
    ?viewProperty dc:identifier ?id.
    optional {
        ?viewProperty dc:format ?content_type
    }
} group by ?c ?class ?content_type order by ?rank
''' % type_string

            views = list(self.vocab.query(view_query, initNs=dict(whyis=self.NS.whyis, dc=self.NS.dc)))
            if len(views) == 0:
                print("Cannot find template %s for %s using types %s." % (view, resource.identifier, types))
                abort(404)
            headers = {'Content-Type': "text/html"}
            extension = views[0]['view'].value.split(".")[-1]
            if extension in DATA_EXTENSIONS:
                headers['Content-Type'] = DATA_EXTENSIONS[extension]
            if views[0]['content_type'] is not None:
                headers['Content-Type'] = views[0]['content_type']
            print("rendering template: %s"% views[0]['view'].value)
            return render_template(views[0]['view'].value, **template_args), 200, headers
        self.render_view = render_view

        # Register blueprints
        self.register_blueprint(nanopub_blueprint)
        self.register_blueprint(sparql_blueprint)
        self.register_blueprint(entity_blueprint)
        #self.register_blueprint(tableview_blueprint)
        for p in self.plugins:
            if p.blueprint is not None:
                print("Registering Blueprint",str(p.blueprint))
                with p.plugin_context():
                    self.register_blueprint(p.blueprint)
        

    def get_entity_uri(self, name, format):
        content_type = None
        if format is not None:
            if format in DATA_EXTENSIONS:
                content_type = DATA_EXTENSIONS[format]
            else:
                name = '.'.join([name, format])
        if name is not None:
            entity = self.NS.local[name]
        elif 'uri' in request.args:
            entity = URIRef(request.args['uri'])
        else:
            entity = self.NS.local.Home
        return entity, content_type

    def get_send_file_max_age(self, filename):
        if self.debug:
            return 0
        else:
            return Empty.get_send_file_max_age(self, filename)
