# -*- coding:utf-8 -*-
import lit

import os
import sys, collections
from empty import Empty
from flask import Flask, render_template, g, session, redirect, url_for, request, flash, abort
import flask_ld as ld
from flask_ld.utils import lru
from flask_restful import Resource

from flask_admin import Admin, BaseView, expose

import rdflib
from flask_security import Security, \
    UserMixin, RoleMixin, login_required
from flask_security.core import current_user
from flask_login import AnonymousUserMixin, login_user
from flask_security.forms import RegisterForm
from flask_security.utils import encrypt_password
from werkzeug.datastructures import ImmutableList
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, TextAreaField, StringField, validators
import rdfalchemy
from rdfalchemy.orm import mapper
import sadi
import json
import sadi.mimeparse

from flask_mail import Mail, Message

import database

from datetime import datetime

import markdown

import rdflib.plugin
from rdflib.store import Store
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.query import ResultParser, ResultSerializer, Processor, Result, UpdateProcessor
from rdflib.exceptions import Error
rdflib.plugin.register('sparql', Result,
        'rdflib.plugins.sparql.processor', 'SPARQLResult')
rdflib.plugin.register('sparql', Processor,
        'rdflib.plugins.sparql.processor', 'SPARQLProcessor')
rdflib.plugin.register('sparql', UpdateProcessor,
        'rdflib.plugins.sparql.processor', 'SPARQLUpdateProcessor')

# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))

basestring = getattr(__builtins__, 'basestring', str)

class NamespaceContainer:
    @property
    def prefixes(self):
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Namespace):
                result[key] = value
        return result

from rdfalchemy import *
from flask_ld.datastore import *

# Setup Flask-Security
class ExtendedRegisterForm(RegisterForm):
    identifier = TextField('Identifier', [validators.Required()])
    givenName = TextField('Given Name', [validators.Required()])
    familyName = TextField('Family Name', [validators.Required()])

# Form for full-text search
class SearchForm(Form):
    search_query = StringField('search_query', [validators.DataRequired()])

def to_json(result):
    return json.dumps([dict([(key, value.value if isinstance(value, Literal) else value) for key, value in x.items()]) for x in result.bindings])


class App(Empty):

    def _top_classes(self):

        import rdflib.plugin
        from rdflib.store import Store
        from rdflib.parser import Parser
        from rdflib.serializer import Serializer
        from rdflib.query import ResultParser, ResultSerializer, Processor, Result, UpdateProcessor
        from rdflib.exceptions import Error
        rdflib.plugin.register('sparql', Result,
                               'rdflib.plugins.sparql.processor', 'SPARQLResult')
        rdflib.plugin.register('sparql', Processor,
                               'rdflib.plugins.sparql.processor', 'SPARQLProcessor')
        rdflib.plugin.register('sparql', UpdateProcessor,
                               'rdflib.plugins.sparql.processor', 'SPARQLUpdateProcessor')

        retr_query = '''
construct {
  ?subClass rdfs:subClassOf ?id;
            a ?type;
            rdfs:label ?sclabel.
  ?id rdfs:label ?label;
      a ?idtype.
} where {
    {
       ?subClass rdfs:subClassOf ?id.
    }
    optional {
       ?subClass a ?type.
    }
    optional {
        ?subClass rdfs:label ?sclabel.
    }
    optional {
        ?id rdfs:label ?label
    }
    optional {
        ?id a ?idtype.
    }
}'''
        g = self.db.query(retr_query).graph

        #print list(g[::self.NS.sio.object])

        query = '''

select distinct ?id where {
    {
       ?subClass rdfs:subClassOf ?id.
    }
    ?id rdfs:label ?label.
    optional {
        ?id rdfs:subClassOf ?superClass.
    }
    FILTER (!bound(?superClass))
    FILTER (isURI(?id))
} order by ?label'''
        return [g.resource(i[0]) for i in g.query(query)]



#full-text search
    def search(self, term):
        import rdflib.plugin
        from rdflib.store import Store
        from rdflib.parser import Parser
        from rdflib.serializer import Serializer
        from rdflib.query import ResultParser, ResultSerializer, Processor, Result, UpdateProcessor
        from rdflib.exceptions import Error
        rdflib.plugin.register('sparql', Result,
                               'rdflib.plugins.sparql.processor', 'SPARQLResult')
        rdflib.plugin.register('sparql', Processor,
                               'rdflib.plugins.sparql.processor', 'SPARQLProcessor')
        rdflib.plugin.register('sparql', UpdateProcessor,
                               'rdflib.plugins.sparql.processor', 'SPARQLUpdateProcessor')

        search_query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX bds: <http://www.bigdata.com/rdf/search#>
PREFIX hbgd: <%s>

select distinct ?uri ?name ?type ?score ?text where{
    ?term bds:search "%s" .
    ?term bds:relevance ?score .
    ?uri rdfs:label ?term .
    { ?uri a hbgd:HBGDkiConcept ;
      optional{ ?uri skos:definition ?text . }
      BIND(hbgd:HBGDkiConcept as ?type)
      BIND(?term as ?name)
    } UNION
    { ?uri a hbgd:Question ;
           rdfs:label ?term ;
      optional{ ?uri prov:value ?text . }
      BIND(hbgd:Question as ?type)
      BIND(?term as ?name)
    } UNION
    { ?uri a ?type ;
           rdfs:label ?name ;
           prov:value|skos:definition ?term .
      BIND(?term as ?text)
    }
} order by DESC(?score)''' % (self.NS.hbgd, term)
        r = self.db.query(search_query)
        condensed = []
        included = set()
        for row in r:
            if row['uri'] not in included:
                included.add(row['uri'])
                condensed.append(row)
        return condensed



    def configure_database(self):
        """
        Database configuration should be set here
        """
        self.NS = NamespaceContainer()
        self.NS.RDFS = rdflib.RDFS
        self.NS.RDF = rdflib.RDF
        self.NS.rdfs = rdflib.Namespace(rdflib.RDFS)
        self.NS.rdf = rdflib.Namespace(rdflib.RDF)
        self.NS.owl = rdflib.OWL
        self.NS.xsd   = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
        self.NS.dc    = rdflib.Namespace("http://purl.org/dc/terms/")
        self.NS.dcelements    = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
        self.NS.auth  = rdflib.Namespace("http://vocab.rpi.edu/auth/")
        self.NS.foaf  = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
        self.NS.prov  = rdflib.Namespace("http://www.w3.org/ns/prov#")
        self.NS.skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
        self.NS.cmo = rdflib.Namespace("http://purl.org/twc/ontologies/cmo.owl#")
        self.NS.sio = rdflib.Namespace("http://semanticscience.org/resource/")
        self.NS.sioc_types = rdflib.Namespace("http://rdfs.org/sioc/types#")
        self.NS.sioc = rdflib.Namespace("http://rdfs.org/sioc/ns#")
        self.NS.np = rdflib.Namespace("http://www.nanopub.org/nschema#")
        self.NS.graphene = rdflib.Namespace("http://vocab.rpi.edu/graphene/")
        self.NS.local = rdflib.Namespace(self.config['lod_prefix']+'/')
        self.NS.ov = rdflib.Namespace("http://open.vocab.org/terms/")


        self.db = database.engine_from_config(self.config, "db_")
        load_namespaces(self.db,locals())
        Resource.db = self.db

        self.vocab = Graph()
        #print URIRef(self.config['vocab_file'])
        self.vocab.load(open(self.config['vocab_file']), format="turtle")

        self.role_api = ld.LocalResource(self.NS.prov.Role,"role", self.db.store, self.vocab, self.config['lod_prefix'], RoleMixin)
        self.Role = self.role_api.alchemy

        self.user_api = ld.LocalResource(self.NS.prov.Agent,"user", self.db.store, self.vocab, self.config['lod_prefix'], UserMixin)
        self.User = self.user_api.alchemy

        self.nanopub_api = ld.LocalResource(self.NS.np.Nanopublication,"pub", self.db.store, self.vocab, self.config['lod_prefix'], name="Graph")
        self.Nanopub = self.nanopub_api.alchemy

        self.classes = mapper(self.Role, self.User)
        self.datastore = RDFAlchemyUserDatastore(self.db, self.classes, self.User, self.Role)
        self.security = Security(self, self.datastore,
                                 register_form=ExtendedRegisterForm)
        #self.mail = Mail(self)


    def configure_views(self):

        def sort_by(resources, property):
            return sorted(resources, key=lambda x: x.value(property))

        class InvitedAnonymousUser(AnonymousUserMixin):
            '''A user that has been referred via kikm references but does not have a user account.'''
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

        @self.before_request
        def load_forms():
            #g.search_form = SearchForm()
            g.ns = self.NS
            g.get_summary = get_summary
            g.get_entity = get_entity
            g.rdflib = rdflib
            g.isinstance = isinstance

        @self.login_manager.user_loader
        def load_user(user_id):
            if user_id != None:
                return self.datastore.find_user(id=user_id)
            else:
                return None
        extensions = {
            "rdf": "application/rdf+xml",
            "json": "application/ld+json",
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
            "text/turtle" : "turtle",
            "application/trig" : "trig",
            "application/n-quads" : "nquads",
            "application/n-triples" : "nt",
            None: "json-ld"
        }

        def get_graphs(graphs):
            query = 'select ?s ?p ?o ?g where {graph ?g {?s ?p ?o} } values ?g { %s }'
            query = query % ' '.join([graph.n3() for graph in graphs])
            print query
            quads = self.db.store.query(query)
            result = Dataset()
            result.addN(quads)
            return result

        def get_entity(entity):
            nanopubs = self.db.query('''select distinct ?s ?p ?o ?g where {
            ?np np:hasAssertion?|np:hasProvenance?|np:hasPublicationInfo? ?g;
                sio:isAbout ?e.
            graph ?g {?s ?p ?o.}
        }''',initBindings={'e':entity}, initNs={'np':self.NS.np, 'sio':self.NS.sio})
            result = ConjunctiveGraph()
            result.addN(nanopubs)
            print result.serialize(format="trig")
            return result.resource(entity)

        self.get_entity = get_entity

        def get_summary(resource):
            summary_properties = [
                self.NS.skos.definition,
                self.NS.dc.abstract,
                self.NS.dc.description,
                self.NS.RDFS.comment,
                self.NS.dcelements.description
            ]
            return resource.graph.preferredLabel(resource.identifier, default=[], labelProperties=summary_properties)

        self.get_summary = get_summary

        @self.route('/about.<format>')
        @self.route('/about')
        @self.route('/<name>.<format>')
        @self.route('/<name>')
        @self.route('/')
        @login_required
        def view(name=None, format=None, view=None):
            #print name
            if name is not None:
                entity = self.NS.local[name]
            elif 'uri' in request.args:
                entity = URIRef(request.args['uri'])
            else:
                entity = self.NS.local.Home
            content_type = request.headers['Accept'] if 'Accept' in request.headers else '*/*'
            if format is not None and format in extensions:
                content_type = extensions[format]

            if entity is not self.NS.local.Home:
        		print lit.getfullname(entity)
            resource = get_entity(entity)
            print resource.identifier, content_type

            htmls = set(['application/xhtml','text/html'])
            if sadi.mimeparse.best_match(htmls, content_type) in htmls:
                print lit.getfullname(resource.identifier)
                print resource.identifier
                return render_view(resource)
            else:
                fmt = dataFormats[sadi.mimeparse.best_match([mt for mt in dataFormats.keys() if mt is not None],content_type)]
                return resource.graph.serialize(format=fmt)
                

        def render_view(resource):
            template_args = dict(ns=self.NS,
                                 this=resource, g=g,
                                 current_user=current_user,
                                 isinstance=isinstance,
                                 get_entity=get_entity,
                                 get_summary=get_summary,
                                 rdflib=rdflib,
                                 hasattr=hasattr,
                                 set=set)
            view = None
            if 'view' in request.args:
                view = request.args['view']
            # 'view' is the default view
            content = resource.value(self.NS.sioc.content)
            if (view == 'view' or view is None) and content is not None:
                if content is not None:
                    return render_template('content_view.html',content=content, **template_args)
            value = resource.value(self.NS.prov.value)
            if value is not None and view is None:
                headers = {}
                headers['ContentType'] = 'text/plain'
                content_type = resource.value(self.NS.ov.hasContentType)
                if content_type is not None:
                    headers['ContentType'] = content_type
                if value.datatype == XSD.base64Binary:
                    return base64.b64decode(value.value), 200, headers
                if value.datatype == XSD.hexBinary:
                    return binascii.unhexlify(value.value), 200, headers
                return value.value, 200, headers

            if view is None:
                view = 'view'

            if 'as' in request.args:
                types = [URIRef(request.args['as'])]
            else:
                types = list(resource[RDF.type])
            #if len(types) == 0:
            types.append(self.NS.RDFS.Resource)
            #print types
            type_string = ' '.join([x.n3() if hasattr(x,'n3') else x.identifier.n3() for x in types])
            view_query = '''select ?id ?view ?rank where {
    {
        select ?class (count(?mid) as ?rank) where {
            ?c rdfs:subClassOf* ?mid.
            ?mid rdfs:subClassOf* ?class.
        } group by ?class ?c order by ?class ?c
    }
    ?class ?viewProperty ?view.
    ?viewProperty rdfs:subPropertyOf* graphene:hasView.
    ?viewProperty dc:identifier ?id.
} order by ?rank
values ?c { %s }
''' % type_string

            #print view_query
            views = list(self.vocab.query(view_query, initNs=dict(graphene=self.NS.graphene, dc=self.NS.dc),
                                          initBindings=dict(id=Literal(view))))
            if len(views) == 0:
                views = list(self.vocab.query(view_query, initNs=dict(graphene=self.NS.graphene, dc=self.NS.dc),
                                          initBindings=dict(id=Literal(view))))
            #print views
            if len(views) == 0:
                abort(404)

            # default view (list of nanopubs)
            # if available, replace with class view
            # if available, replace with instance view
            return render_template(views[0]['view'].value, **template_args)

        @self.route('/comments')
        @login_required
        def latest_comments():
            query = '''select distinct ?thing ?creator (max(?c) as ?created) where {
  ?comment a <http://rdfs.org/sioc/types#Comment>;
           <http://semanticscience.org/resource/isAbout> ?thing;
           <http://purl.org/dc/terms/created> ?c;
           <http://www.w3.org/ns/prov#wasAttributedTo> ?creator.
  filter(isURI(?thing))
} group by ?thing ?creator order by desc(?created) limit 20'''
            entries = {}
            entry_list = []
            for thing, creator, created in self.db.query(query):
                if thing not in entries:
                    entry = dict(thing=self.db.resource(thing), creator=self.db.resource(creator), created=created)
                    entries[thing] = entry
                    entry_list.append(entry)
            return render_template('latest_comments.html', ns=self.NS, entries=entry_list, g=g, current_user=current_user)

        # @self.route('/<name>/comment', methods=['GET', 'POST'])
        # @login_required
        # def comments(name):
        #     this = self.NS.local[name]
        #     if request.method == 'POST':
        #         inputGraph = ConjunctiveGraph()
        #         contentType = request.headers['Content-Type']
        #         inputGraph.parse(data=request.data,format="json-ld")
        #         processed_graph = ConjunctiveGraph()
        #         comment_id = ld.create_id()
        #         comment_uri = URIRef("%s/comment/%s#assertion" % (this, comment_id))
        #         processed_graph += ld.rebase(inputGraph, URIRef("urn:nanopub#"), comment_uri)
        #         comment = processed_graph.resource(comment_uri)
        #         comment.add(self.NS.RDF.type, self.NS.sioc_types.Comment)
        #         comment.add(self.NS.dc.created, Literal(datetime.utcnow()))
        #         comment.add(self.NS.prov.wasAttributedTo, current_user.resUri)
        #         comment.add(self.NS.sio['isAbout'], this)
        #         print processed_graph.serialize(format='turtle')
        #         if comment.value(self.NS.sioc.reply_of):
        #             comment.value(self.NS.sioc.reply_of).add(self.NS.sioc.has_reply, comment)
        #         comment.add(self.NS.prov.wasAttributedTo, current_user.resUri)
        #         comment_text = comment.value(self.NS.prov.value)
        #         rendered_comment = markdown.markdown(comment_text, extensions=['rdfa'])
        #         comment.add(self.NS.sioc.content, Literal(rendered_comment))

        #         pub_info = ConjunctiveGraph(self.db.store,URIRef("%s/pub/%s" % (this, comment_id)))

        @self.route('/ns/search_results/<query>')
        @login_required
        def search_results(query):
            results = self.search(query)
            return render_template('search_results.html', ns=self.NS, query=query, results=results, sort_by=sort_by, current_user=current_user)

        self.api = ld.LinkedDataApi(self, "", self.db.store, "")


        self.admin = Admin(self, name="graphene", template_mode='bootstrap3')
        self.admin.add_view(ld.ModelView(self.nanopub_api, default_sort=RDFS.label))
        self.admin.add_view(ld.ModelView(self.role_api, default_sort=RDFS.label))
        self.admin.add_view(ld.ModelView(self.user_api, default_sort=foaf.familyName))

        app = self
        class NanopublicationResource(ld.LinkedDataResource):
            decorators = [login_required]

            def __init__(self):
                self.local_resource = app.nanopub_api

            def _can_edit(self, uri):
                if current_user.has_role('Publisher') or current_user.has_role('Editor'):
                    return True
                if (uri +"#assertion", app.NS.prov.wasAttributedTo, current_user.resUri) in app.db:
                    return True
                return False

            def _get_uri(self, ident):
                return URIRef('%s/pub/%s'%(app.config['lod_prefix'], ident))

            def get(self, ident):
                uri = self._get_uri(ident)
                if not self._can_edit(uri):
                    return app.login_manager.unauthorized()
                result = self.local_resource.read(uri)
                #print result
                return result

            def delete(self, ident):
                uri = self._get_uri(ident)
                if not self._can_edit(uri):
                    return app.login_manager.unauthorized()
                self.local_resource.delete(uri)
                return '', 204

            def _prepare_nanopub(self, nanopub):
                #nanopub = graph.resource(nanopub_uri)
                processed_graph = nanopub.graph
                nanopub.add(app.NS.RDF.type, app.NS.np.Nanopublication)

                nanopub_assertion = nanopub.value(app.NS.np.hasAssertion)
                about = nanopub.value(app.NS.sio['isAbout'])
                self._prep_graph(nanopub_assertion, about=about)

                nanopub_provenance = nanopub.value(app.NS.np.hasProvenance)
                self._prep_graph(nanopub_provenance, about=nanopub_assertion.identifier)

                nanopub_pubinfo = nanopub.value(app.NS.np.hasPublicationInfo)
                self._prep_graph(nanopub_pubinfo, about=nanopub_assertion.identifier)

                return nanopub_assertion, nanopub_provenance, nanopub_pubinfo

            def put(self,ident):
                uri = self._get_uri(ident)
                #print uri
                if not self._can_edit(uri):
                    return app.login_manager.unauthorized()
                inputGraph = Graph()
                contentType = request.headers['Content-Type']
                sadi.deserialize(inputGraph,request.data,contentType)

                nanopub = inputGraph.resource(URIRef(uri+"_assertion"))
                nanopub_text = nanopub.value(app.NS.prov.value)
                rendered_nanopub = markdown.markdown(nanopub_text, extensions=['rdfa'])
                nanopub.set(app.NS.sioc.content, Literal(rendered_nanopub))
                nanopub.set(app.NS.dc.modified,Literal(datetime.utcnow()))
                if nanopub.value(app.NS.sioc.reply_of):
                    nanopub.value(app.NS.sioc.reply_of).add(app.NS.sioc.has_reply, nanopub)

                self.local_resource.update(uri, inputGraph)
                return '', 201

            def post(self, ident=None):
                if ident is not None:
                    return self.put(ident)
                else:
                    default_prefix = URIRef('urn:nanopub')
                    inputGraph = ConjunctiveGraph()
                    contentType = request.headers['Content-Type']

                    sadi.deserialize(inputGraph, request.data, contentType)
                    nanopub_id = ld.create_id()
                    nanopub_uri = app.NS.local["pub/%s" % nanopub_id]
                    processed_graph = ConjunctiveGraph()
                    nanopub_graph = ConjunctiveGraph(identifier=nanopub_uri, store=processed_graph.store)
                    quads = [x for x in ld.rebase(inputGraph, default_prefix, nanopub_uri)]
                    processed_graph.addN(quads)

                    assertion, provenance, pubinfo = self._prepare_nanopub(nanopub_graph.resource(nanopub_uri))

                    pubinfo_graph = Graph(processed_graph.store, pubinfo.identifier)

                    assertion_in_pubinfo = pubinfo_graph.resource(assertion.identifier)
                    assertion_in_pubinfo.add(app.NS.dc.created, Literal(datetime.utcnow()))
                    assertion_in_pubinfo.add(app.NS.dc.contributor, current_user.resUri)

                    #print "Adding a nanopublication"
                    print processed_graph.serialize(format="trig")

                    app.db.addN(processed_graph.quads())

                return '', 201


            def _prep_graph(self, resource, about = None):
                #print '_prep_graph', resource.identifier, about
                content_type = resource.value(app.NS.ov.hasContentType)
                #print resource.graph.serialize(format="nquads")
                g = Graph(store=resource.graph.store,identifier=resource.identifier)
                text = resource.value(app.NS.prov.value)
                if content_type is not None and text is not None:
                    #print 'Content type:', content_type, resource.identifier
                    html = None
                    if content_type.value in ["text/html", "application/xhtml+xml"]:
                        html = Literal(text.value, datatype=RDF.HTML)
                    if content_type.value == 'text/markdown':
                        #print "Aha, markdown!"
                        #print text.value
                        html = markdown.markdown(text.value, extensions=['rdfa'])
                        attributes = ['vocab="%s"' % app.NS.local,
                                      'base="%s"'% app.NS.local,
                                      'prefix="%s"' % ' '.join(['%s: %s'% x for x in app.NS.prefixes.items()])]
                        if about is not None:
                            attributes.append('resource="%s"' % about)
                        html = '<div %s>%s</div>' % (' '.join(attributes), html)
                        html = Literal(html, datatype=RDF.HTML)
                        text = html
                        content_type = "text/html"
                    if html is not None:
                        resource.add(app.NS.sioc.content, html)
                        try:
                            g.parse(data=text, format='rdfa')
                        except:
                            pass
                    else:
                        try:
                            sadi.deserialize(g, text, content_type)
                        except:
                            pass
                #print Graph(store=resource.graph.store).serialize(format="trig")


        self.api.add_resource(NanopublicationResource, '/pub', '/pub/<ident>')

def config_str_to_obj(cfg):
    if isinstance(cfg, basestring):
        module = __import__('config', fromlist=[cfg])
        return getattr(module, cfg)
    return cfg


def app_factory(config, app_name, blueprints=None):
    # you can use Empty directly if you wish
    app = App(app_name)
    config = config_str_to_obj(config)
    #print dir(config)
    app.configure(config)
    if blueprints:
        app.add_blueprint_list(blueprints)
    app.setup()

    return app


def heroku():
    from config import Config, project_name
    # setup app through APP_CONFIG envvar
    return app_factory(Config, project_name)
