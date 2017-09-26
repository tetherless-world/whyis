import sadi
import rdflib
import setlr
from datetime import datetime
from nanopub import Nanopublication


graphene = rdflib.Namespace('http://vocab.rpi.edu/graphene/')
np = rdflib.Namespace("http://www.nanopub.org/nschema#")
prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
dc = rdflib.Namespace("http://purl.org/dc/terms/")
sio = rdflib.Namespace("http://semanticscience.org/resource/")
setl = rdflib.Namespace("http://purl.org/twc/vocab/setl/")

class Service(sadi.Service):

    activity_class = graphene.Agent
    
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
        np_assertions = list(i.graph.subjects(rdflib.RDF.type, np.Assertion))
        activity = nanopub.provenance.resource(rdflib.BNode())
        activity.add(rdflib.RDF.type, self.activity_class)
        nanopub.pubinfo.add((o.identifier, rdflib.RDF.type, self.getOutputClass()))
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))
        for assertion in np_assertions:
            nanopub.provenance.add((activity.identifier, prov.used, assertion))
            nanopub.provenance.add((nanopub.assertion.identifier, prov.wasDerivedFrom, assertion))
            nanopub.pubinfo.add((nanopub.assertion.identifier, dc.created, rdflib.Literal(datetime.utcnow())))

    def getInstances(self, graph):
        return [graph.resource(i) for i, in graph.query(self.get_query())]
    
    def process_graph(self, inputGraph):
        outputGraph = rdflib.ConjunctiveGraph()

        instances = self.getInstances(inputGraph)
        for i in instances:
            og = rdflib.Graph(store=outputGraph.store, identifier=rdflib.BNode().skolemize())
            #OutputClass = sadi.OntClass(og,self.getOutputClass())
            o = og.resource(i.identifier) # OutputClass(i.identifier)
            result = self.process(i, o)
            if len(list(og.subjects(rdflib.RDF.type, np.Nanopublication))) == 0:
                new_np = Nanopublication(store=og.store)
                new_np.add((new_np.identifier, rdflib.RDF.type, np.Nanopublication))
                new_np.add((new_np.identifier, np.hasAssertion, og.identifier))
                new_np.add((og.identifier, rdflib.RDF.type, np.Assertion))
            for new_np in self.app.nanopub_manager.prepare(outputGraph):
                if len(new_np.assertion) == 0:
                    continue
                self.explain(new_np, i, o)
                new_np.add((new_np.identifier, sio.isAbout, i.identifier))
                self.app.nanopub_manager.publish(new_np)
        return outputGraph

class UpdateChangeService(Service):
    @property
    def query_predicate(self):
        return graphene.updateChangeQuery             

class GlobalChangeService(Service):
    @property
    def query_predicate(self):
        return graphene.globalChangeQuery

        
class Crawler(UpdateChangeService):

    activity_class = graphene.GraphCrawl

    def __init__(self, depth=-1, predicates=[None]):
        self.depth = depth
        self.predicates = predicates
    
    def getInputClass(self):
        return graphene.CrawlerStart

    def getOutputClass(self):
        return graphene.Crawled
    
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
            node = self.app.get_resource(uri)
            cache.add(uri)
            if depth != 0:
                for p in self.predicates:
                    todo.extend([(x.identifier, depth-1) for x in node[p]])

class OntologyImporter(GlobalChangeService):

    activity_class = graphene.OntologyImport
        
    def getInputClass(self):
        return OWL.Ontology

    def getOutputClass(self):
        return graphene.ImportedOntology

    def process(self, i, o):
        pass
                    
class SETLr(UpdateChangeService):

    activity_class = setl.SemanticETL
    

    def __init__(self, depth=-1, predicates=[None]):
        self.depth = depth
        self.predicates = predicates
    
    def getInputClass(self):
        return setl.SemanticETLScript

    def getOutputClass(self):
        return graphene.ProcessedSemanticETLScript
    
    def get_query(self):
        return '''select ?resource where { ?resource a %s.}''' % self.getInputClass().n3()
    
    def explain(self, nanopub, i, o):
        np_assertions = list(i.graph.subjects(rdflib.RDF.type, np.Assertion))
        activity = nanopub.provenance.resource(rdflib.BNode())
        activity.add(rdflib.RDF.type, i.identifier)
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))
        for assertion in np_assertions:
            nanopub.provenance.add((activity.identifier, prov.used, assertion))
            nanopub.provenance.add((nanopub.assertion.identifier, prov.wasDerivedFrom, assertion))
            nanopub.pubinfo.add((nanopub.assertion.identifier, prov.wasAttributedTo, i.identifier))
            nanopub.pubinfo.add((nanopub.assertion.identifier, prov.wasAttributedTo, i.identifier))
    
    def process(self, i, o):
        setl_graph = i.graph
        resources = setlr._setl(setl_graph)
        # retire old copies
        old_np_map = {}
        for new_np, assertion, orig in  self.app.db.query('''select ?np ?assertion ?original_uri where {
    ?np np:hasAssertion ?assertion.
    ?assertion a np:Assertion;
        prov:wasGeneratedBy/a ?setl;
        prov:wasQuotedFrom ?original_uri.
}''', initBindings=dict(setl=i.identifier), initNs=dict(prov=prov, np=np)):
            old_np_map[orig] = assertion
            self.app.nanopub_manager.retire(new_np)
            #print resources
        for output_graph in setl_graph.subjects(prov.wasGeneratedBy, i.identifier):
            out = resources[output_graph]
            out_conjunctive = rdflib.ConjunctiveGraph(store=out.store, identifier=output_graph)
            #print "Generated graph", out.identifier, len(out), len(out_conjunctive)
            mappings = {}
            for new_np in self.app.nanopub_manager.prepare(out_conjunctive, mappings=mappings):
                self.explain(new_np, i, o)
                orig = [orig for orig, new in mappings.items() if new == new_np.assertion.identifier]
                if len(orig) == 0:
                    continue
                orig = orig[0]
                if isinstance(orig, rdflib.URIRef):
                    new_np.pubinfo.add((new_np.assertion.identifier, prov.wasQuotedFrom, orig))
                    if orig in old_np_map:
                        new_np.pubinfo.add((new_np.assertion.identifier, prov.wasRevisionOf, old_np_map[orig]))
                #print "Nanopub assertion has", len(new_np.assertion), "statements."
                self.app.nanopub_manager.publish(new_np)
                
