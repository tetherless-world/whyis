from __future__ import print_function
import sadi
import rdflib
import setlr
from datetime import datetime
from nanopub import Nanopublication
import flask_ld as ld
import flask
from flask import render_template
from flask import render_template_string
import logging

import sys, traceback

import database

import tempfile

from depot.io.interfaces import StoredFile

whyis = rdflib.Namespace('http://vocab.rpi.edu/whyis/')
whyis = rdflib.Namespace('http://vocab.rpi.edu/whyis/')
np = rdflib.Namespace("http://www.nanopub.org/nschema#")
prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
dc = rdflib.Namespace("http://purl.org/dc/terms/")
sio = rdflib.Namespace("http://semanticscience.org/resource/")
setl = rdflib.Namespace("http://purl.org/twc/vocab/setl/")
pv = rdflib.Namespace("http://purl.org/net/provenance/ns#")
skos = rdflib.Namespace("http://www.w3.org/2008/05/skos#")

class Service(sadi.Service):

    dry_run = False
    
    activity_class = whyis.Agent
    
    def get_query(self):
        return '''select ?resource where {
    ?resource rdf:type/rdfs:subClassOf* %s.
    filter not exists { ?resource rdf:type/rdfs:subClassOf* %s. }
}''' % (self.getInputClass().n3(), self.getOutputClass().n3())
    
    def annotateServiceDescription(self, desc):
        desc.add(self.query_predicate, rdflib.Literal(self.get_query()))

    def processGraph(self,content, type):
        inputGraph = sadi.SADIGraph()
        self.deserialize(inputGraph, content, type)
        return process

    def explain(self, nanopub, i, o):
        activity = nanopub.provenance.resource(rdflib.BNode())
        activity.add(rdflib.RDF.type, self.activity_class)
        nanopub.pubinfo.add((o.identifier, rdflib.RDF.type, self.getOutputClass()))
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))

    def getInstances(self, graph):
        if hasattr(graph.store, "nsBindings"):
            graph.store.nsBindings = {}
        prefixes = self.app.NS.prefixes
        if hasattr(self, 'prefixes'):
            prefixes = self.prefixes
        return [graph.resource(i) for i, in graph.query(self.get_query(), initNs=prefixes)]
    
    def process_graph(self, inputGraph):
        instances = self.getInstances(inputGraph)
        results = []
        for i in instances:
            print("Processing", i.identifier, self)
            output_nanopub = Nanopublication()
            o = output_nanopub.assertion.resource(i.identifier) # OutputClass(i.identifier)
            error = False
            try:
                result = self.process_nanopub(i, o, output_nanopub)
            except Exception as e:
                output_nanopub.add((output_nanopub.assertion.identifier,self.app.NS.sioc.content, rdflib.Literal(str(e))))
                logging.exception("Error processing resource %s in nanopub %s"%(i.identifier, inputGraph.identifier))
                error = True
            print("Output Graph", output_nanopub.identifier, len(output_nanopub))
            for new_np in self.app.nanopub_manager.prepare(rdflib.ConjunctiveGraph(store=output_nanopub.store)):
                if len(new_np.assertion) == 0 and not error:
                    continue
                self.explain(new_np, i, o)
                new_np.add((new_np.identifier, sio.isAbout, i.identifier))
                #print new_np.serialize(format="trig")
                if not self.dry_run:
                    self.app.nanopub_manager.publish(new_np)
                results.append(new_np)
        return results

    def process_nanopub(self, i, o, output_nanopub):
        self.process(i, o)
    
class UpdateChangeService(Service):
    @property
    def query_predicate(self):
        return whyis.updateChangeQuery
    
    def explain(self, nanopub, i, o):
        np_assertions = list(i.graph.subjects(rdflib.RDF.type, np.Assertion))
        activity = nanopub.provenance.resource(rdflib.BNode())
        nanopub.pubinfo.add((o.identifier, rdflib.RDF.type, self.getOutputClass()))
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))
        for assertion in np_assertions:
            nanopub.provenance.add((activity.identifier, prov.used, assertion))
            nanopub.provenance.add((nanopub.assertion.identifier, prov.wasDerivedFrom, assertion))
            nanopub.pubinfo.add((nanopub.assertion.identifier, dc.created, rdflib.Literal(datetime.utcnow())))

class GlobalChangeService(Service):
    @property
    def query_predicate(self):
        return whyis.globalChangeQuery

class Crawler(UpdateChangeService):

    activity_class = whyis.GraphCrawl

    def __init__(self, depth=-1, predicates=[None], node_type=whyis.CrawlerStart, output_node_type=whyis.Crawled):
        self.depth = depth
        self.node_type = node_type
        self.output_node_type = output_node_type
        self.predicates = predicates
    
    def getInputClass(self):
        return self.node_type

    def getOutputClass(self):
        return self.output_node_type
    
    def get_query(self):
        return '''select ?resource where {
    ?resource rdf:type/rdfs:subClassOf* %s.
}''' % self.getInputClass().n3()

    def process(self, i, o):
        cache = set()
        todo = [(i.identifier, self.depth)]
        # this non-recursive form does a BFS of the linked data graph.
        while len(todo) > 0:
            uri, depth = todo.pop()
            #print uri, depth, len(todo)
            if uri in cache:
                continue
            node = None
            node = self.app.get_resource(uri, async=False)
            cache.add(uri)
            if depth != 0:
                for p in self.predicates:
                    todo.extend([(x.identifier, depth-1) for x in node[p]])


class EmailNotifier(UpdateChangeService):

    activity_class = whyis.EmailNotification

    def __init__(self, input_type, subject_template, body_template=None, html_template=None, user_predicate=prov.wasAssociatedWith, output_type=whyis.Notified):
        self.body_template = body_template
        self.html_template = html_template
        self.input_type = input_type
        self.output_type = output_type
        self.user_predicate = user_predicate

    def getInputClass(self):
        return self.input_type

    def getOutputClass(self):
        return self.output_type

    def process(self, i, o):
        with self.app.mail.connect() as conn:
            for u in i[self.user_predicate]:
                user = self.datastore.find_user(id=u.identifier)
                parameters = dict(user=user, resource=i)
                args = {
                    'recipients':[user.email],
                    'subject' : render_template_string(self.subject_template, user=user, resource=i)
                }
                if self.body_template is not None:
                    args['body'] = render_template_string(self.body_template, user=user, resource=i)
                if self.html_template is not None:
                    args['html'] = render_template_string(self.html_template, user=user, resource=i)
                msg = Message(**args)
                conn.send(msg)

                    
class ImporterCrawler(UpdateChangeService):
    activity_class = whyis.ImporterGraphCrawl

    def getInputClass(self):
        return whyis.ImporterResource

    def getOutputClass(self):
        return whyis.ImportedResource

    _query = None
    
    def get_query(self):
        if self._query is None:
            prefixes = [x.detect_url for x in self.app.config['namespaces']]
            self._query = '''select distinct ?resource where {
  graph ?assertion {
    {?s ?p ?resource . } union {?resource ?p ?o}
  }
  FILTER (regex(str(?resource), "^(%s)")) .
  filter not exists {
    ?assertion prov:wasGeneratedBy [ a whyis:KnowledgeImport].
  }
} ''' % '|'.join(prefixes)
            print(self._query)

        return self._query

    def process(self, i, o):
        node = self.app.run_importer(i.identifier)

class DatasetImporter(UpdateChangeService):
    activity_class = whyis.ImportDatasetEntities

    def getInputClass(self):
        return whyis.DatasetEntity

    def getOutputClass(self):
        return whyis.ImportedDatasetEntity

    _query = None
    
    def get_query(self):
        if self._query is None:
            prefixes = [x.detect_url for x in self.app.config['namespaces']]
            self._query = '''select distinct ?resource where {
  ?resource void:inDataset ?dataset.
  FILTER (regex(str(?resource), "^(%s)")) .
  filter not exists {
    ?assertion prov:wasQuotedFrom ?resource.
  }
} ''' % '|'.join(prefixes)
            print(self._query)

        return self._query

    def process(self, i, o):
        node = self.app.run_importer(i.identifier)
                    
                            
class OntologyImporter(UpdateChangeService):

    activity_class = whyis.OntologyImport
    
    def get_query(self):
        return '''select ?resource where {
    ?ontology owl:imports ?resource.
}'''
            
    def getInputClass(self):
        return rdflib.OWL.Ontology

    def getOutputClass(self):
        return whyis.ImportedOntology

    def process_nanopub(self, i, o, new_np):
        if (i.identifier, rdflib.RDF.type, whyis.ImportedOntology) in self.app.db:
            print("Skipping already imported ontology:", i.identifier)
            return
        print("Attempting to import", i.identifier)
        file_format = rdflib.util.guess_format(i.identifier)
        try: # Try the best guess at a format.
            g = rdflib.Graph()
            g.parse(location=i.identifier, format=file_format, publicID=self.app.NS.local)
            g.serialize() # to test that parsing was actually successful.
            for s,p,o in g:
                new_np.assertion.add((s,p,o))
            logging.debug("%s was parsed as %s"%(i.identifier,file_format))
            print("%s was parsed as %s"%(i.identifier,file_format))
            print(len(new_np.assertion), len(g))
        except Exception: # If that doesn't work, brute force it with all possible RDF formats, most likely first.
            print("Could not parse %s as %s" %(i.identifier,file_format))
            #traceback.print_exc(file=sys.stdout)
            parsed = False
            for f in ['xml', 'turtle', 'trig', # Most likely
                      'n3','nquads','nt', # rarely used for ontologies, but sometimes
                      'json-ld', # occasionally used
                      'hturtle', 'trix', # uncommon
                      'rdfa1.1','rdfa1.0','rdfa', # rare, but I've seen them.
                      'mdata','microdata','html']: # wow, there are a lot of RDF formats...
                try:
                    #print "Trying", f
                    g = rdflib.Graph()
                    g.parse(location=i.identifier, format=f, publicID=self.app.NS.local)
                    g.serialize() # to test that parsing was actually successful.
                    for s,p,o in g:
                        new_np.assertion.add((s,p,o))
                    logging.debug("%s was parsed as %s"%(i.identifier, f))
                    print("%s was parsed as %s"%(i.identifier, f))
                    parsed = True
                    break
                except Exception:
                    print("BF: Could not parse %s as %s" %(i.identifier,f))
                    #traceback.print_exc(file=sys.stdout)
                    pass
            if not parsed: # probably the best guess anyways, retry to throw the best possible exception.
                print("Could not import ontology %s" % i.identifier)
                return
                #g = rdflib.Graph()
                #g.parse(location=i.identifier, format=file_format, publicID=self.app.NS.local)
                #g.serialize() # to test that parsing was actually successful.
        
        new_np.pubinfo.add((new_np.assertion.identifier, self.app.NS.prov.wasQuotedFrom, i.identifier))
        new_np.add((new_np.identifier, self.app.NS.sio.isAbout, i.identifier))

class SETLMaker(GlobalChangeService):
    activity_class = setl.Planner

    def getInputClass(self):
        return pv.File

    def getOutputClass(self):
        return setl.SETLedFile

    def get_query(self):
        return '''
prefix setl: <http://purl.org/twc/vocab/setl/>
select distinct ?resource where {
    graph ?type_assertion {
      ?resource rdf:type/rdfs:subClassOf* ?parameterized_type.
    }
    graph ?assertion {
      ?setl_script rdfs:subClassOf setl:SemanticETLScript;
        rdfs:subClassOf [ a owl:Restriction;
            owl:onProperty prov:used;
            owl:someValuesFrom ?parameterized_type
        ].
    }
    filter not exists {
        ?type_assertion prov:wasGeneratedBy [ a setl:Planner].
    }
    filter not exists {
        ?assertion prov:wasGeneratedBy [ a setl:Planner].
    }
    filter not exists {
        ?planned_assertion prov:wasDerivedFrom* ?assertion;
           prov:wasGeneratedBy [ a setl:Planner].
        graph ?planned_assertion {
            ?setl_run a ?setl_script.
            ?extract prov:used ?resource.
        }
    }
  filter (!regex(str(?resource), "^bnode:"))
}'''

    def process_nanopub(self, i, o, new_np):
        print(i.identifier)
        p = self.app.NS.prov.used
        for script, np, parameterized_type, type_assertion in self.app.db.query('''
prefix setl: <http://purl.org/twc/vocab/setl/>
select distinct ?setl_script ?np ?parameterized_type ?type_assertion where {
    graph ?assertion {
      ?setl_script rdfs:subClassOf setl:SemanticETLScript;
        rdfs:subClassOf [ a owl:Restriction;
            owl:onProperty prov:used;
            owl:someValuesFrom ?parameterized_type
      ].
    }
    graph ?type_assertion { ?resource rdf:type/rdfs:subClassOf* ?parameterized_type. }
    ?type_np a np:Nanopublication; np:hasAssertion ?type_assertion.
    ?np a np:Nanopublication; np:hasAssertion ?assertion.
    filter not exists {
        ?type_assertion prov:wasGeneratedBy [ a setl:Planner].
    }
    filter not exists {
        ?assertion prov:wasGeneratedBy [ a setl:Planner].
    }
    filter not exists {
        ?planned_assertion prov:wasDerivedFrom* ?assertion;
           prov:wasGeneratedBy [ a setl:Planner].
        graph ?planned_assertion {
            ?setl_run a ?setl_script.
            ?extract prov:used ?resource.
        }
    }
}''', initBindings=dict(resource=i.identifier), initNs=self.app.NS.prefixes):
            nanopub = self.app.nanopub_manager.get(np)
            print("Template NP", nanopub.identifier, len(nanopub))
            template_prefix = nanopub.assertion.value(script, setl.hasTemplatePrefix)
            replacement_prefix = self.app.NS.local['setl/'+ld.create_id()+"/"]

            mappings = {}
            for x, in nanopub.assertion.query("select ?x where {?x a ?t}",
                                              initBindings={'t':parameterized_type},
                                              initNs=self.app.NS.prefixes):
                mappings[x] = i.identifier
            
            script_run = rdflib.URIRef(script.replace(template_prefix, replacement_prefix, 1))
            for x, in nanopub.assertion.query("select ?x where {?x a ?t}",
                                              initBindings={'t':script},
                                              initNs=self.app.NS.prefixes):
                mappings[x] = script_run
            def replace(x):
                if x in mappings:
                    return mappings[x]
                if isinstance(x, rdflib.URIRef) and x.startswith("bnode:"):
                    return rdflib.BNode(x.replace("bnode:","",1))
                if isinstance(x, rdflib.URIRef) and x == script:
                    return script
                if isinstance(x, rdflib.URIRef) and x.startswith(template_prefix):
                    return rdflib.URIRef(x.replace(template_prefix, replacement_prefix, 1))
                return x
            for s, p, o in nanopub.assertion:
                new_np.assertion.add((replace(s), replace(p), replace(o)))
            new_np.assertion.add((script_run, rdflib.RDF.type, script))
            new_np.assertion.add((script_run, rdflib.RDF.type, setl.SemanticETLScript))
            new_np.provenance.add((new_np.assertion.identifier, prov.wasDerivedFrom, nanopub.assertion.identifier))
            new_np.provenance.add((new_np.assertion.identifier, prov.wasDerivedFrom, type_assertion))
            print("Instance NP", new_np.identifier, len(new_np))
#            print new_np.serialize(format="trig")

setlr_handlers_added = False

class SETLr(UpdateChangeService):

    activity_class = setl.SemanticETL
    

    def __init__(self, depth=-1, predicates=[None]):
        self.depth = depth
        self.predicates = predicates

        global setlr_handlers_added                       
        if not setlr_handlers_added:
            def _whyis_content_handler(location):
                resource = self.app.get_resource(location)
                fileid = resource.value(self.app.NS.whyis.hasFileID)
                if fileid is not None:
                    return self.app.file_depot.get(fileid)
            setlr.content_handlers.insert(0,_whyis_content_handler)
            setlr_handlers_added = True
    
    def getInputClass(self):
        return setl.SemanticETLScript

    def getOutputClass(self):
        return whyis.ProcessedSemanticETLScript
    
    def get_query(self):
        return '''select distinct ?resource where { ?resource a %s.}''' % self.getInputClass().n3()
    
    def explain(self, nanopub, i, o):
        np_assertions = list(i.graph.subjects(rdflib.RDF.type, np.Assertion)) + [nanopub.assertion.identifier]
        activity = nanopub.provenance.resource(rdflib.BNode())
        activity.add(rdflib.RDF.type, i.identifier)
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))
        for assertion in np_assertions:
            nanopub.provenance.add((activity.identifier, prov.used, assertion))
            nanopub.provenance.add((nanopub.assertion.identifier, prov.wasDerivedFrom, assertion))
            nanopub.pubinfo.add((nanopub.assertion.identifier, prov.wasAttributedTo, i.identifier))
            nanopub.pubinfo.add((nanopub.assertion.identifier, prov.wasAttributedTo, i.identifier))

    def process(self, i, o):
        
        query_store = database.create_query_store(self.app.db.store)
        db_graph = rdflib.ConjunctiveGraph(store=query_store)
        db_graph.NS = self.app.NS
        setlr.actions[whyis.sparql] = db_graph
        setlr.actions[whyis.NanopublicationManager] = self.app.nanopub_manager
        setlr.actions[whyis.Nanopublication] = self.app.nanopub_manager.new
        setl_graph = i.graph
#        setlr.run_samples = True
        resources = setlr._setl(setl_graph)
        # retire old copies
        old_np_map = {}
        to_retire = []
        for new_np, assertion, orig in self.app.db.query('''select distinct ?np ?assertion ?original_uri where {
    ?np np:hasAssertion ?assertion.
    ?assertion a np:Assertion;
        prov:wasGeneratedBy/a ?setl;
        prov:wasQuotedFrom ?original_uri.
}''', initBindings=dict(setl=i.identifier), initNs=dict(prov=prov, np=np)):
            old_np_map[orig] = assertion
            to_retire.append(new_np)
            if len(to_retire) > 100:
                self.app.nanopub_manager.retire(*to_retire)
                to_retire = []
        self.app.nanopub_manager.retire(*to_retire)
            #print resources
        for output_graph in setl_graph.subjects(prov.wasGeneratedBy, i.identifier):
            if setl_graph.resource(output_graph)[rdflib.RDF.type:whyis.NanopublicationCollection]:
                self.app.nanopub_manager.publish(resources[output_graph])
            else:
                out = resources[output_graph]
                out_conjunctive = rdflib.ConjunctiveGraph(store=out.store, identifier=output_graph)
                #print "Generated graph", out.identifier, len(out), len(out_conjunctive)
                nanopub_prepare_graph = rdflib.ConjunctiveGraph(store="Sleepycat")
                nanopub_prepare_graph_tempdir = tempfile.mkdtemp()
                nanopub_prepare_graph.store.open(nanopub_prepare_graph_tempdir, True)
    
                mappings = {}

                to_publish = []
                triples = 0
                for new_np in self.app.nanopub_manager.prepare(out_conjunctive, mappings=mappings, store=nanopub_prepare_graph.store):
                    self.explain(new_np, i, o)
                    orig = [orig for orig, new in mappings.items() if new == new_np.assertion.identifier]
                    if len(orig) == 0:
                        continue
                    orig = orig[0]
                    print(orig)
                    if isinstance(orig, rdflib.URIRef):
                        new_np.pubinfo.add((new_np.assertion.identifier, prov.wasQuotedFrom, orig))
                        if orig in old_np_map:
                            new_np.pubinfo.add((new_np.assertion.identifier, prov.wasRevisionOf, old_np_map[orig]))
                    print("Publishing %s with %s assertions." % (new_np.identifier, len(new_np.assertion)))
                    to_publish.append(new_np)
            
                #triples += len(new_np)
                #if triples > 10000:
                self.app.nanopub_manager.publish(*to_publish)
            print('Published')
        for input_file in setl_graph.objects(None, prov.used):
            if input_file in resources:
                i = resources[input_file]
                if isinstance(i, StoredFile):
                    print "Closing", input_file
                    i.close()

class Deductor(UpdateChangeService):
    def __init__(self, where, construct, explanation, resource="?resource", prefixes=None): # prefixes should be 
        if resource is not None:
            self.resource = resource
	self.prefixes = {}
        if prefixes is not None:
            self.prefixes = prefixes
        self.where = where
        self.construct = construct
        self.explanation = explanation

    def getInputClass(self):
        return pv.File # input and output class should be customized for the specific inference

    def getOutputClass(self):
        return setl.SETLedFile

    def get_query(self):
        self.app.db.store.nsBindings={}
        return '''SELECT DISTINCT %s WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\n}''' %( self.resource, self.where, self.construct )
    
    def get_context(self, i):
        context = {}
        context_vars = self.app.db.query('''SELECT DISTINCT * WHERE {\n%s\nFILTER(str(%s)="%s") .\n}''' %( self.where, self.resource, i.identifier) , initNs=self.app.NS.prefixes )
        for key in context_vars.json["results"]["bindings"][0].keys():
            context[key]=context_vars.json["results"]["bindings"][0][key]["value"]
        return context
    
    def process(self, i, o):
        npub = Nanopublication(store=o.graph.store)
        triples = self.app.db.query('''CONSTRUCT {\n%s\n} WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\nFILTER(str(%s)="%s") .\n}''' %( self.construct, self.where, self.construct, self.resource, i.identifier) , initNs=self.prefixes ) 
        for s, p, o, c in triples:
            print("Deductor Adding ", s, p, o)
            npub.assertion.add((s, p, o))
        npub.provenance.add((npub.assertion.identifier, prov.value, rdflib.Literal(flask.render_template_string(self.explanation,**self.get_context(i)))))

    def __str__(self):
        return "Deductor Instance: " + str(self.__dict__)
