# -*- coding:utf-8 -*-
import importlib

import os
import sys
from empty import Empty
from flask import render_template, g, redirect, url_for, request, flash, Response, \
    send_from_directory, make_response, abort
from functools import lru_cache, wraps

import jinja2

from nanopub import NanopublicationManager
import requests
from re import finditer
import pytz

from werkzeug.exceptions import Unauthorized
from werkzeug.utils import secure_filename

from depot.manager import DepotManager
from depot.middleware import FileServeApp

import rdflib
from rdflib import Literal, Graph, Namespace, URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.query import Processor, Result, UpdateProcessor

from flask_security import Security, login_required
from flask_security.core import current_user
from flask_security.forms import RegisterForm
from flask_wtf import Form
from wtforms import TextField, StringField, validators
import sadi
import json
import sadi.mimeparse
from slugify import slugify

from urllib.parse import urlencode

from celery import Celery
from celery.schedules import crontab
from celery.task.control import inspect

import database

from datetime import datetime

from datastore import WhyisUserDatastore

import markdown
import search
from whyis import filters

from whyis.namespace import NS

#from flask_login.config import EXEMPT_METHODS

rdflib.plugin.register('sparql', Result,
        'rdflib.plugins.sparql.processor', 'SPARQLResult')
rdflib.plugin.register('sparql', Processor,
        'rdflib.plugins.sparql.processor', 'SPARQLProcessor')
rdflib.plugin.register('sparql', UpdateProcessor,
        'rdflib.plugins.sparql.processor', 'SPARQLUpdateProcessor')

# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))

# we create some comparison keys:
# increase probability that the rule will be near or at the top
top_compare_key = False, -100, [(-2, 0)]
# increase probability that the rule will be near or at the bottom 
bottom_compare_key = True, 100, [(2, 0)]


# Setup Flask-Security
class ExtendedRegisterForm(RegisterForm):
    id = TextField('Identifier', [validators.Required()])
    givenName = TextField('Given Name', [validators.Required()])
    familyName = TextField('Family Name', [validators.Required()])

def to_json(result):
    return json.dumps([ {key: value.value if isinstance(value, Literal) else value for key, value in list(x.items())} for x in result.bindings])

def conditional_login_required(func):
    from flask import current_app
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in ['OPTIONS']:# EXEMPT_METHODS:
            return func(*args, **kwargs)
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        if 'DEFAULT_ANONYMOUS_READ' in current_app.config and current_app.config['DEFAULT_ANONYMOUS_READ']:
            return func(*args, **kwargs)
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view

class App(Empty):

    managed = False
    
    def configure_extensions(self):

        Empty.configure_extensions(self)
        self.celery = Celery(self.name, broker=self.config['CELERY_BROKER_URL'], beat=True)
        self.celery.conf.update(self.config)
        
        app = self

        self.redis = self.celery.broker_connection().default_channel.client
        
        if 'root_path' in self.config:
            self.root_path = self.config['root_path']
        
        if 'WHYIS_TEMPLATE_DIR' in self.config and app.config['WHYIS_TEMPLATE_DIR'] is not None:
            my_loader = jinja2.ChoiceLoader(
                [jinja2.FileSystemLoader(p) for p in self.config['WHYIS_TEMPLATE_DIR']] 
                + [app.jinja_loader]
            )
            app.jinja_loader = my_loader
        
        def setup_task(service):
            service.app = app
            print(service)
            result = None
            if service.query_predicate == self.NS.whyis.globalChangeQuery:
                result = process_resource
            else:
                result = process_nanopub
            result.service = lambda : service
            return result

        @self.celery.task
        def process_resource(service_name, taskid=None):
            service = self.config['inferencers'][service_name]
            if is_waiting(service_name):
                print("Deferring to a later invocation.", service_name)
                return
            print(service_name)
            service.process_graph(app.db)

        @self.celery.task
        def process_nanopub(nanopub_uri, service_name, taskid=None):
            service = self.config['inferencers'][service_name]
            print(service, nanopub_uri)
            if app.nanopub_manager.is_current(nanopub_uri):
                nanopub = app.nanopub_manager.get(nanopub_uri)
                service.process_graph(nanopub)
            else:
                print("Skipping retired nanopub", nanopub_uri)

        def setup_periodic_task(task):
            @self.celery.task
            def find_instances():
                print("Triggered task", task['name'])
                for x, in task['service'].getInstances(app.db):
                    task['do'](x)
            
            @self.celery.task
            def do_task(uri):
                print("Running task", task['name'], 'on', uri)
                resource = app.get_resource(uri)

                # result never used
                task['service'].process_graph(resource.graph)

            task['service'].app = app
            task['find_instances'] = find_instances
            task['do'] = do_task

            return task
            
        app.inference_tasks = []
        if 'inference_tasks' in self.config:
            app.inference_tasks = [setup_periodic_task(task) for task in self.config['inference_tasks']]

        for name, task in list(self.config['inferencers'].items()):
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

        def is_waiting(service_name):
            """
            Check if a task is waiting.
            """
            scheduled_tasks = list(inspect().scheduled().values())[0]
            for task in scheduled_tasks:
                if 'kwargs' in task:
                    args = eval(task['kwargs'])
                    if service_name == args.get('service_name',None):
                        return True
            return False
                
        def is_running_waiting(service_name):
            """
            Check if a task is running or waiting.
            """
            if is_waiting(service_name):
                return True
            running_tasks = list(inspect().active().values())[0]
            for task in running_tasks:
                if 'kwargs' in task:
                    args = eval(task['kwargs'])
                    if service_name == args.get('service_name',None):
                        return True
            return False
                        
        @self.celery.task()
        def update(nanopub_uri):
            '''gets called whenever there is a change in the knowledge graph.
            Performs a breadth-first knowledge expansion of the current change.'''
            #print "Updating on", nanopub_uri
            if not app.nanopub_manager.is_current(nanopub_uri):
                print("Skipping retired nanopub", nanopub_uri)
                return
            nanopub = app.nanopub_manager.get(nanopub_uri)
            nanopub_graph = ConjunctiveGraph(nanopub.store)
            if 'inferencers' in self.config:
                for name, service in list(self.config['inferencers'].items()):
                    service.app = self
                    if service.query_predicate == self.NS.whyis.updateChangeQuery:
                        #print "checking", name, nanopub_uri, service.get_query()
                        if service.getInstances(nanopub_graph):
                            print("invoking", name, nanopub_uri)
                            process_nanopub.apply_async(kwargs={'nanopub_uri': nanopub_uri, 'service_name':name}, priority=1 )
                for name, service in list(self.config['inferencers'].items()):
                    service.app = self
                    if service.query_predicate == self.NS.whyis.globalChangeQuery and not is_running_waiting(name):
                        #print "checking", name, service.get_query()
                        process_resource.apply_async(kwargs={'service_name':name}, priority=5)

        def run_update(nanopub_uri):
            update.apply_async(args=[nanopub_uri],priority=9)
        self.nanopub_update_listener = run_update

        def is_waiting_importer(entity_name, exclude=None):
            """
            Check if a task is running or waiting.
            """
            if inspect().scheduled():
                tasks = list(inspect().scheduled().values())
                for task in tasks:
                    if 'args' in task and entity_name in task['args']:
                        return True
            return False

        app = self
        @self.celery.task(retry_backoff=True, retry_jitter=True,autoretry_for=(Exception,),max_retries=4, bind=True)
        def run_importer(self, entity_name):
            entity_name = URIRef(entity_name)
            counter = app.redis.incr(("import",entity_name))
            if counter > 1:
                return
            print('importing', entity_name)
            importer = app.find_importer(entity_name)
            if importer is None:
                return
            importer.app = app
            modified = importer.last_modified(entity_name, app.db, app.nanopub_manager)
            updated = importer.modified(entity_name)
            if updated is None:
                updated = datetime.now(pytz.utc)
            print("Remote modified:", updated, type(updated), "Local modified:", modified, type(modified))
            if modified is None or (updated - modified).total_seconds() > importer.min_modified:
                importer.load(entity_name, app.db, app.nanopub_manager)
            app.redis.set(("import",entity_name),0)
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
        

    def configure_database(self):
        """
        Database configuration should be set here
        """
        self.NS = NS
        self.NS.local = rdflib.Namespace(self.config['lod_prefix']+'/')

        self.admin_db = database.engine_from_config(self.config, "admin_")
        self.db = database.engine_from_config(self.config, "knowledge_")
        self.db.app = self

        self.vocab = ConjunctiveGraph()
        #print URIRef(self.config['vocab_file'])
        default_vocab = Graph(store=self.vocab.store)
        default_vocab.parse("default_vocab.ttl", format="turtle", publicID=str(self.NS.local))
        custom_vocab = Graph(store=self.vocab.store)
        custom_vocab.parse(self.config['vocab_file'], format="turtle", publicID=str(self.NS.local))


        self.datastore = WhyisUserDatastore(self.admin_db, {}, self.config['lod_prefix'])
        self.security = Security(self, self.datastore,
                                 register_form=ExtendedRegisterForm)

        self.file_depot = DepotManager.get('files')
        if self.file_depot is None:
            DepotManager.configure('files', self.config['file_archive'])
            self.file_depot = DepotManager.get('files')
        if DepotManager.get('nanopublications') is None:
            DepotManager.configure('nanopublications', self.config['nanopub_archive'])

    def weighted_route(self, *args, **kwargs):
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
        for importer in self.config['namespaces']:
            if importer.matches(name):
                new_name = importer.map(name)
                #print 'Found mapped URI', new_name
                return new_name, importer
        return None, None

    def find_importer(self, name):
        for importer in self.config['namespaces']:
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
                result = self._graph.store.subgraph({ "term" : { "graphs.@graph.@id" : str(self.identifier) } })
##                try:
#                result = Graph()
##                try:
                new_graph = Graph();
                for quad in result.query('''
construct {
    ?e ?p ?o.
    ?o rdfs:label ?label.
    ?o skos:prefLabel ?prefLabel.
    ?o dc:title ?title.
    ?o foaf:name ?name.
    ?o ?pattr ?oatter.
    ?oattr rdfs:label ?oattrlabel
} where {
    graph ?g {
      ?e ?p ?o.
    }
    ?g a np:Assertion.
    optional {
      ?e sio:hasAttribute|sio:hasPart ?o.
      ?o ?pattr ?oattr.
      optional {
        ?oattr rdfs:label ?oattrlabel.
      }
    }
    optional {
      ?o rdfs:label ?label.
    }
    optional {
      ?o skos:prefLabel ?prefLabel.
    }
    optional {
      ?o dc:title ?title.
    }
    optional {
      ?o foaf:name ?name.
    }
}''', initNs=NS.prefixes, initBindings={'e':self.identifier}):
                    new_graph.add(quad[:3])
#                        s,p,o = quad
#                    else:
#                        # Last term is never used
#                        s,p,o,_ = quad
#                    result.add((s,p,o))
#                except:
#                    pass
                self._description = new_graph.resource(self.identifier)

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
            print(entity, importer)

            if importer is not None:
                modified = importer.last_modified(entity, self.db, self.nanopub_manager)
                if modified is None or async_ is False:
                    self.run_importer(entity)
                elif not importer.import_once:
                    print("Type of modified is",type(modified))
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
        fileid = self.file_depot.create(f.stream, f.filename, f.mimetype)
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
    ?nanopub np:hasAssertion ?assertion.
    ?assertion dc:contributor ?user.
}''', initBindings=dict(nanopub=uri, user=current_user.identifier), initNs=dict(np=self.NS.np, dc=self.NS.dc)):
            return True
        return False

    def configure_views(self):

        def sort_by(resources, property):
            return sorted(resources, key=lambda x: x.value(property))

        def camel_case_split(identifier):
            matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
            return [m.group(0) for m in matches]

        label_properties = [self.NS.skos.prefLabel, self.NS.RDFS.label, self.NS.schema.name, self.NS.dc.title, self.NS.foaf.name, self.NS.schema.name]

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
                    #print "skipping", db
                    continue
                for property in label_properties:
                    labels = self.lang_filter(resource_entity[property])
                    if len(labels) > 0:
                        return labels[0]
                    
                if len(labels) == 0:
                    name = [x.value for x in [resource_entity.value(self.NS.foaf.givenName),
                                              resource_entity.value(self.NS.foaf.familyName)] if x is not None]
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
                labels = self.lang_filter(resource[property])
                #print "mem", property, label
                if len(labels) > 0:
                    return labels[0]
            return get_remote_label(resource.identifier)
            
        @self.before_request
        def load_forms():
            if 'authenticators' in self.config:
                for authenticator in self.config['authenticators']:
                    user = authenticator.authenticate(request, self.datastore, self.config)
                    if user is not None:
                    #    login_user(user)
                        break
                
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

        extensions = {
            "rdf": "application/rdf+xml",
            "jsonld": "application/ld+json",
            "json": "application/json",
            "ttl": "text/turtle",
            "trig": "application/trig",
            "turtle": "text/turtle",
            "owl": "application/rdf+xml",
            "nq": "application/n-quads",
            "nt": "application/n-triples",
            "html": "text/html"
        }

        dataFormats = {
            "application/rdf+xml" : "xml",
            "application/ld+json" : 'json-ld',
            "application/json" : 'json-ld',
            "text/turtle" : "turtle",
            "application/trig" : "trig",
            "application/n-quads" : "nquads",
            "application/n-triples" : "nt",
            "application/rdf+json" : "json",
            "text/html" : None,
            "application/xhtml+xml" : None,
            "application/xhtml" : None,
            None: "json-ld"
        }

        htmls = set(['application/xhtml','text/html', 'application/xhtml+xml'])


        def get_graphs(graphs):
            query = '''select ?s ?p ?o ?g where {
                hint:Query hint:optimizer "Runtime" .

                graph ?g {?s ?p ?o}
                } values ?g { %s }'''
            query = query % ' '.join([graph.n3() for graph in graphs])
            #print query
            quads = self.db.store.query(query, initNs=self.NS.prefixes)
            result = rdflib.Dataset()
            result.addN(quads)
            return result

        def explain(graph):
            values = ')\n  ('.join([' '.join([x.n3() for x in triple]) for triple in graph.triples((None,None,None))])
            values = 'VALUES (?s ?p ?o)\n{\n('+ values + ')\n}'
            
            try:
                nanopubs = self.db.query('''select distinct ?np where {
    hint:Query hint:optimizer "Runtime" .
    ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
        np:hasPublicationInfo ?pubinfo;
        np:hasAssertion ?assertion;
    graph ?assertion { ?s ?p ?o.}
}''' + values, initNs=self.NS.prefixes)
                result = ConjunctiveGraph()
                for nanopub_uri, in nanopubs:
                    self.nanopub_manager.get(nanopub_uri, result)
            except Exception as e:
                print(str(e), entity)
                raise e
            return result.resource(entity)
        
        def get_entity_sparql(entity):
            try:
                statements = self.db.query('''select distinct ?s ?p ?o ?g where {
    hint:Query hint:optimizer "Runtime" .
            ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
                np:hasPublicationInfo ?pubinfo;
                np:hasAssertion ?assertion;

            {graph ?np { ?np sio:isAbout ?e.}}
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
            
        
        def get_entity_disk(entity):
            try:
                nanopubs = self.db.query('''select distinct ?np where {
    hint:Query hint:optimizer "Runtime" .
            ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
                np:hasPublicationInfo ?pubinfo;
                np:hasAssertion ?assertion;

            {graph ?np { ?np sio:isAbout ?e.}}
            UNION
            {graph ?assertion { ?e ?p ?o.}}
        }''',initBindings={'e':entity}, initNs=self.NS.prefixes)
                result = ConjunctiveGraph()
                for nanopub_uri, in nanopubs:
                    self.nanopub_manager.get(nanopub_uri, result)
#                result.addN(nanopubs)
            except Exception as e:
                print(str(e), entity)
                raise e
            #print result.serialize(format="trig")
            return result.resource(entity)

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

        @self.route('/sparql', methods=['GET', 'POST'])
        @conditional_login_required
        def sparql_view():
            has_query = False
            for arg in list(request.args.keys()):
                if arg.lower() == "update":
                    return "Update not allowed.", 403
                if arg.lower() == 'query':
                    has_query = True
            if request.method == 'GET' and not has_query:
                return redirect(url_for('sparql_form'))
            #print self.db.store.query_endpoint
            if request.method == 'GET':
                headers = {}
                headers.update(request.headers)
                if 'Content-Length' in headers:
                    del headers['Content-Length']
                req = requests.get(self.db.store.query_endpoint,
                                   headers = headers, params=request.args)
            elif request.method == 'POST':
                if 'application/sparql-update' in request.headers['content-type']:
                    return "Update not allowed.", 403
                #print(request.get_data())
                req = requests.post(self.db.store.query_endpoint, data=request.get_data(),
                                    headers = request.headers, params=request.args)
            #print self.db.store.query_endpoint
            #print req.status_code
            response = Response(req.content, content_type = req.headers['content-type'])
            #response.headers[con(req.headers)
            return response, req.status_code
        
        @self.route('/sparql.html')
        @conditional_login_required
        def sparql_form():
            
            template_args = dict(ns=self.NS,
                                 g=g,
                                 config=self.config,
                                 current_user=current_user,
                                 isinstance=isinstance,
                                 rdflib=rdflib,
                                 hasattr=hasattr,
                                 set=set)

            return render_template('sparql.html',endpoint="/sparql", **template_args)

        
        if 'WHYIS_CDN_DIR' in self.config and self.config['WHYIS_CDN_DIR'] is not None:
            @self.route('/cdn/<path:filename>')
            def cdn(filename):
                return send_from_directory(self.config['WHYIS_CDN_DIR'], filename)

        @self.route('/about.<format>', methods=['GET','POST','DELETE'])
        @self.weighted_route('/<path:name>', compare_key=bottom_compare_key, methods=['GET','POST','DELETE'])
        @self.weighted_route('/<path:name>.<format>', compare_key=bottom_compare_key, methods=['GET','POST','DELETE'])
        @self.route('/', methods=['GET','POST','DELETE'])
        @self.route('/home', methods=['GET','POST','DELETE'])
        @self.route('/about', methods=['GET','POST','DELETE'])
        @conditional_login_required
        def view(name=None, format=None, view=None):
            self.db.store.nsBindings = {}
            content_type = None
            if format is not None:
                if format in extensions:
                    content_type = extensions[format]
                else:
                    name = '.'.join([name, format])
            #argstring = '&'.join(["%s=%s"%(k,v) for k,v in request.args.iteritems(multi=True) if k != 'value'])
            if name is not None:
                #if len(argstring) > 0:
                #    name = name + "?" + argstring
                entity = self.NS.local[name]
            elif 'uri' in request.args:
                entity = URIRef(request.args['uri'])
            else:
                entity = self.NS.local.Home

            #print(request.method, 'view()', entity, view)
            if request.method == 'POST':
                print ("uploading file",entity)
                if len(request.files) == 0:
                    flash('No file uploaded')
                    return redirect(request.url)
                upload_type = rdflib.URIRef(request.form['upload_type'])
                self.add_files(entity, [y for x, y in request.files.items(multi=True)],
                               upload_type=upload_type)
                url = "/about?%s" % urlencode(dict(uri=str(entity), view="view"))
                print ("redirecting to",url)
                return redirect(url)
            elif request.method == 'DELETE':
                self.delete_file(entity)
                return '', 204
            elif request.method == 'GET':
                resource = self.get_resource(entity)

                # 'view' is the default view
                fileid = resource.value(self.NS.whyis.hasFileID)
                if fileid is not None and 'view' not in request.args:
                    print (resource.identifier, fileid)
                    f = self.file_depot.get(fileid)
                    fsa = FileServeApp(f, self.config["file_archive"].get("cache_max_age",3600*24*7))
                    return fsa
            
                if content_type is None:
                    content_type = request.headers['Accept'] if 'Accept' in request.headers else 'text/turtle'
                #print entity

                fmt = sadi.mimeparse.best_match([mt for mt in list(dataFormats.keys()) if mt is not None],content_type)
                if 'view' in request.args or fmt in htmls:
                    return render_view(resource)
                elif fmt in dataFormats:
                    print('attempting linked data on', name, fmt, dataFormats[fmt], format, content_type)
                    output_graph = ConjunctiveGraph()
                    result, status, headers = render_view(resource, view='describe')
                    output_graph.parse(data=result, format="json-ld")
                    return output_graph.serialize(format=dataFormats[fmt]), 200, {'Content-Type':content_type}
                #elif 'view' in request.args or sadi.mimeparse.best_match(htmls, content_type) in htmls:
                else:
                    return render_view(resource)
                
        views = {}
        def render_view(resource, view=None, args=None):
            template_args = dict()
            template_args.update(self.template_imports)
            template_args.update(dict(
                ns=self.NS,
                this=resource, g=g,
                current_user=current_user,
                isinstance=isinstance,
                args=request.args if args is None else args,
                url_for=url_for,
                get_entity=get_entity,
                get_summary=get_summary,
                search = search,
                rdflib=rdflib,
                config=self.config,
                hasattr=hasattr,
                set=set))
            if view is None and 'view' in request.args:
                view = request.args['view']

            if view is None:
                view = 'view'

            types = []
            if 'as' in request.args:
                types = [URIRef(request.args['as']), 0]

            types.extend((x, 1) for x in self.vocab[resource.identifier : NS.RDF.type])
            if not types: # KG types cannot override vocab types. This should keep views stable where critical.
                types.extend([(x.identifier, 1) for x in resource[NS.RDF.type]])
            #if len(types) == 0:
            types.append([self.NS.RDFS.Resource, 100])
            type_string = ' '.join(["(%s %d '%s')" % (x.n3(), i, view) for x, i in types])
            view_query = '''select ?id ?view (count(?mid)+?priority as ?rank) ?class ?c where {
    values (?c ?priority ?id) { %s }
    ?c rdfs:subClassOf* ?mid.
    ?mid rdfs:subClassOf* ?class.
    ?class ?viewProperty ?view.
    ?viewProperty rdfs:subPropertyOf* whyis:hasView.
    ?viewProperty dc:identifier ?id.
} group by ?c ?class order by ?rank
''' % type_string

            #print view_query
            views = list(self.vocab.query(view_query, initNs=dict(whyis=self.NS.whyis, dc=self.NS.dc)))
            if len(views) == 0:
                abort(404)

            headers = {'Content-Type': "text/html"}
            extension = views[0]['view'].value.split(".")[-1]
            if extension in extensions:
                headers['Content-Type'] = extensions[extension]
                

            # default view (list of nanopubs)
            # if available, replace with class view
            # if available, replace with instance view
            return render_template(views[0]['view'].value, **template_args), 200, headers
        self.render_view = render_view

        def render_nanopub(data, code, headers=None):
            if data is None:
                return make_response("<h1>Not Found</h1>", 404)

            entity = app.Entity(ConjunctiveGraph(data.store), data.identifier)
            entity.nanopub = data
            data, code, headers = render_view(entity)
            resp = make_response(data, code)
            resp.headers.extend(headers or {})
            return resp

        app = self

        self.nanopub_manager = NanopublicationManager(app.db.store,
                                                      Namespace('%s/pub/'%(app.config['lod_prefix'])),
                                                      self,
                                                      update_listener=self.nanopub_update_listener)

        def _get_graph():
            inputGraph = ConjunctiveGraph()
            contentType = request.headers['Content-Type']
            encoding = 'utf8' if not request.content_encoding else request.content_encoding
            content = str(request.data, encoding)
            fmt = sadi.mimeparse.best_match([mt for mt in list(dataFormats.keys()) if mt is not None],contentType)
            if fmt in dataFormats:
                inputGraph.parse(data=content, format=dataFormats[fmt])
            return inputGraph

        
        #decorators = [conditional_login_required]

        def _get_uri(ident):
            return URIRef('%s/pub/%s'%(app.config['lod_prefix'], ident))

        @self.route('/pub/<ident>',methods=['GET'])
        @self.route('/pub/<ident>.<format>', methods=['GET'])
        @conditional_login_required
        def get_nanopub(ident, format=None):
            #print(request.method, 'get_nanopub()', ident)
            ident = ident.split("_")[0]
            uri = _get_uri(ident)
            result = app.nanopub_manager.get(uri)
            if result is None:
                #print("cannot find", uri)
                abort(404)

            content_type = None
                        
            if format is not None and format in extensions:
                content_type = extensions[format]
            if content_type is None:
                content_type = request.headers['Accept'] if 'Accept' in request.headers else 'application/ld+json'
            fmt = sadi.mimeparse.best_match([mt for mt in list(dataFormats.keys()) if mt is not None],content_type)
            if 'view' in request.args or fmt in htmls:
                return render_nanopub(result, 200)
            elif fmt in dataFormats:
                response = Response(result.serialize(format=dataFormats[fmt]))
                response.headers = {'Content-type': fmt}
                return response, 200

        @self.route('/pub/<ident>', methods=['DELETE'])
        @login_required
        def delete_nanopub(ident):
            #print(request.method, 'delete_nanopub()', ident)
            ident = ident.split("_")[0]
            uri = _get_uri(ident)
            if not app._can_edit(uri):
                return '<h1>Not Authorized</h1>', 401
            app.nanopub_manager.retire(uri)
            return '', 204


        @self.route('/pub/<ident>', methods=['PUT'])
        @login_required
        def put_nanopub(ident):
            #print(request.method, 'put_nanopub()', ident)
            nanopub_uri = _get_uri(ident)
            inputGraph = _get_graph()
            old_nanopub = _prep_nanopub(nanopub_uri, inputGraph)
            for nanopub in app.nanopub_manager.prepare(inputGraph):
                nanopub.pubinfo.set((nanopub.assertion.identifier, app.NS.prov.wasRevisionOf, old_nanopub.assertion.identifier))
                app.nanopub_manager.retire(nanopub_uri)
                app.nanopub_manager.publish(nanopub)

        def _prep_nanopub(nanopub):
            #nanopub = Nanopublication(store=graph.store, identifier=nanopub_uri)
            about = nanopub.nanopub_resource.value(app.NS.sio.isAbout)
            #print nanopub.assertion_resource.identifier, about
            _prep_graph(nanopub.assertion_resource, about.identifier if about is not None else None)
            #_prep_graph(nanopub.pubinfo_resource, nanopub.assertion_resource.identifier)
            _prep_graph(nanopub.provenance_resource, nanopub.assertion_resource.identifier)
            nanopub.pubinfo.add((nanopub.assertion.identifier, app.NS.dc.contributor, current_user.identifier))

            return nanopub

        @self.route('/pub/<ident>',  methods=['POST'])
        @self.route('/pub',  methods=['POST'])
        @login_required
        def post_nanopub(ident=None):
            #print(request.method, 'post_nanopub()', ident)
            if ident is not None:
                return self.put(ident)
            inputGraph = _get_graph()
            #for nanopub_uri in inputGraph.subjects(rdflib.RDF.type, app.NS.np.Nanopublication):
                #nanopub.pubinfo.add((nanopub.assertion.identifier, app.NS.dc.created, Literal(datetime.utcnow())))
            headers = {}
            for nanopub in app.nanopub_manager.prepare(inputGraph):
                _prep_nanopub(nanopub)
                headers['Location'] = nanopub.identifier
                app.nanopub_manager.publish(nanopub)

            return '', 201, headers


        def _prep_graph(resource, about = None):
            #print '_prep_graph', resource.identifier, about
            content_type = resource.value(app.NS.ov.hasContentType)
            if content_type is not None:
                content_type = content_type.value
            #print 'graph content type', resource.identifier, content_type
            #print resource.graph.serialize(format="nquads")
            g = Graph(store=resource.graph.store,identifier=resource.identifier)
            text = resource.value(app.NS.prov.value)
            if content_type is not None and text is not None:
                #print 'Content type:', content_type, resource.identifier
                html = None
                if content_type in ["text/html", "application/xhtml+xml"]:
                    html = Literal(text.value, datatype=NS.RDF.HTML)
                if content_type == 'text/markdown':
                    #print "Aha, markdown!"
                    #print text.value
                    html = markdown.markdown(text.value)
                    attributes = ['vocab="%s"' % app.NS.local,
                                  'base="%s"'% app.NS.local,
                                  'prefix="%s"' % ' '.join(['%s: %s'% x for x in list(app.NS.prefixes.items())])]
                    if about is not None:
                        attributes.append('resource="%s"' % about)
                    html = '<div %s>%s</div>' % (' '.join(attributes), html)
                    html = Literal(html, datatype=NS.RDF.HTML)
                    text = html
                    content_type = "text/html"
                #print resource.identifier, content_type
                if html is not None:
                    resource.set(app.NS.sioc.content, html)
                    try:
                        g.remove((None,None,None))
                        g.parse(data=text, format='rdfa', publicID=app.NS.local)
                    except:
                        pass
                else:
                    #print "Deserializing", g.identifier, 'as', content_type
                    #print dataFormats
                    if content_type in dataFormats:
                        g.parse(data=text, format=dataFormats[content_type], publicID=app.NS.local)
                        #print len(g)
                    #else:
                        #print("not attempting to deserialize.")
#                        try:
#                            sadi.deserialize(g, text, content_type)
#                        except:
#                            pass
            #print Graph(store=resource.graph.store).serialize(format="trig")

    def get_send_file_max_age(self, filename):
        if self.debug:
            return 0
        else:
            return Empty.get_send_file_max_age(self, filename)


from whyis.app_factory import app_factory
from whyis.heroku import heroku

