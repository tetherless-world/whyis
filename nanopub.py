import rdflib
import os
import flask_ld as ld
import collections

np = rdflib.Namespace("http://www.nanopub.org/nschema#")
prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
dc = rdflib.Namespace("http://purl.org/dc/terms/")

class Nanopublication(rdflib.ConjunctiveGraph):

    _nanopub_resource = None
    
    @property
    def nanopub_resource(self):
        if self._nanopub_resource is None:
            self._nanopub_resource = self.resource(self.identifier)
            if not self._nanopub_resource[rdflib.RDF.type : np.Nanopublication]:
                self._nanopub_resource.add(rdflib.RDF.type, np.Nanopublication)
        return self._nanopub_resource
    
    @property
    def assertion_resource(self):
        return self.resource(self.assertion.identifier)
    
    @property
    def pubinfo_resource(self):
        return self.resource(self.pubinfo.identifier)
    
    @property
    def provenance_resource(self):
        return self.resource(self.provenance.identifier)

    _assertion = None
    
    @property
    def assertion(self):
        if self._assertion is None:
            assertion = self.nanopub_resource.value(np.hasAssertion)
            if assertion is None:
                assertion = self.resource(self.identifier+"_assertion")
                assertion.add(rdflib.RDF.type, np.Assertion)
                self.nanopub_resource.add(np.hasAssertion, assertion)
            self._assertion = rdflib.Graph(store=self.store, identifier=assertion)
        return self._assertion

    _pubinfo = None
    
    @property
    def pubinfo(self):
        if self._pubinfo is None:
            pubinfo = self.nanopub_resource.value(np.hasPublicationInfo)
            if pubinfo is None:
                pubinfo = self.resource(self.identifier+"_pubinfo")
                pubinfo.add(rdflib.RDF.type, np.PublicationInfo)
                self.nanopub_resource.add(np.hasPublicationInfo, pubinfo)
            self._pubinfo = rdflib.Graph(store=self.store, identifier=pubinfo)
        return self._pubinfo

    _provenance = None
    
    @property
    def provenance(self):
        if self._provenance is None:
            provenance = self.nanopub_resource.value(np.hasProvenance)
            if provenance is None:
                provenance = self.resource(self.identifier+"_provenance")
                provenance.add(rdflib.RDF.type, np.Provenance)
                self.nanopub_resource.add(np.hasProvenance, provenance)
            self._provenance = rdflib.Graph(store=self.store, identifier=provenance)
        return self._provenance

    @property
    def modified(self):
        modified = self.pubinfo.value(self.assertion.identifier, dc.modified)
        if modified is not None:
            return modified.value


class NanopublicationManager:
    def __init__(self, store, archive_path, prefix, update_listener=None):
        self.db = rdflib.ConjunctiveGraph(store)
        self.store = store
        self.archive_path = archive_path
        self.prefix = rdflib.Namespace(prefix)
        if not os.path.exists(self.archive_path):
            os.makedirs(self.archive_path)
        self.update_listener = update_listener

    def new(self):
        nanopub = Nanopublication(identifier=self.prefix[ld.create_id()])
        nanopub.nanopub_resource
        nanopub.assertion
        nanopub.provenance
        nanopub.pubinfo

        return nanopub
                
    def prepare(self, graph, mappings = None):
        if mappings is None:
            mappings = {}
        new_nps = list(graph.subjects(rdflib.RDF.type, np.Nanopublication))
        if len(new_nps) == 0:
            new_np = Nanopublication(store=graph.store)
            new_np.add((new_np.identifier, rdflib.RDF.type, np.Nanopublication))
            new_np.add((new_np.identifier, np.hasAssertion, graph.identifier))
            new_np.add((graph.identifier, rdflib.RDF.type, np.Assertion))
            new_nps = [new_np.identifier]
        for nanopub in new_nps:
            if self.prefix not in nanopub:
                new_uri = self.prefix[ld.create_id()]
                mappings[nanopub] = new_uri
                for assertion in graph.objects(nanopub, np.hasAssertion):
                    mappings[assertion] = rdflib.URIRef(new_uri+"_assertion")
                for pubinfo in graph.objects(nanopub, np.hasPublicationInfo):
                    mappings[pubinfo] = rdflib.URIRef(new_uri+"_pubinfo")
                for provenance in graph.objects(nanopub, np.hasProvenance):
                    mappings[provenance] = rdflib.URIRef(new_uri+"_provenance")
        #print mappings
                    
        output_graph = rdflib.ConjunctiveGraph()

        for s, p, o, g in graph.quads():
            quad = (mappings.get(s,s), mappings.get(p,p), mappings.get(o,o), mappings.get(g.identifier,g.identifier))
            #print s, p, o, g
            #print quad
            output_graph.add(quad)

        for nanopub_uri in output_graph.subjects(rdflib.RDF.type, np.Nanopublication):
            nanopub = Nanopublication(identifier=nanopub_uri)
            nanopub += output_graph.get_context(nanopub.identifier)
            #print "Nanopub", len(nanopub), len(output_graph.get_context(identifier=nanopub_uri))
            for assertion in output_graph.objects(nanopub.identifier, np.hasAssertion):
                a = nanopub.assertion
                a += output_graph.get_context(identifier=assertion)
                #print "Assertion", len(a), len(output_graph.get_context(identifier=assertion))
            for pubinfo in output_graph.objects(nanopub.identifier, np.hasPublicationInfo):
                p = nanopub.pubinfo
                p += output_graph.get_context(identifier=pubinfo)
                #print "PubInfo", len(p), len(output_graph.get_context(identifier=pubinfo))
            for provenance in output_graph.objects(nanopub.identifier, np.hasProvenance):
                p = nanopub.provenance
                p += output_graph.get_context(identifier=provenance)
                #print "Provenance", len(p), len(output_graph.get_context(identifier=provenance))
            #print "Total", len(output_graph)
            #print "Contexts", [g.identifier for g in output_graph.contexts()]
            yield nanopub
            
    def retire(self, nanopub_uri):
        for np_uri, in self.db.query('''select ?np where {
    ?np (np:hasAssertion/prov:wasDerivedFrom+/^np:hasAssertion)? ?retiree
}''', initNs={"prov":prov, "np":np}, initBindings={"retiree":nanopub_uri}):
            print "Retiring", np_uri, "derived from", nanopub_uri
            nanopub = Nanopublication(store=self.db.store, identifier=np_uri)
            self.db.remove((None,None,None,nanopub.assertion.identifier))
            self.db.remove((None,None,None,nanopub.provenance.identifier))
            self.db.remove((None,None,None,nanopub.pubinfo.identifier))
            self.db.remove((None,None,None,nanopub.identifier))
            self.db.commit()

    def get_path(self, nanopub_uri):
        #print self.prefix, nanopub_uri
        ident = nanopub_uri.replace(self.prefix, "")
        dir_name_length = 3
        path = [ident[i:i+dir_name_length] for i in range(0, len(ident), dir_name_length)]
        return [self.archive_path] + path[:-1] + [ident]
        
    def publish(self, nanopub):
        filepath = self.get_path(nanopub.identifier)
        if not os.path.exists('/'.join(filepath[:-1])):
            os.makedirs('/'.join(filepath[:-1]))
        print "Publishing", nanopub.identifier
        g = rdflib.ConjunctiveGraph(store=nanopub.store)
        g.serialize(open('/'.join(filepath), 'wb'), format="trig")
        for revised in nanopub.pubinfo.objects(nanopub.assertion.identifier, prov.wasRevisionOf):
            for nanopub_uri in self.db.subjects(predicate=np.hasAssertion, object=revised):
                self.retire(nanopub_uri)
        self.db.addN(nanopub.quads())
        self.update_listener(nanopub.identifier)

    def get(self, nanopub_uri, graph = None):
        filepath = self.get_path(nanopub_uri)
        if graph is None:
            graph = rdflib.ConjunctiveGraph()
        nanopub = Nanopublication(store=graph.store, identifier=nanopub_uri)
        nanopub.parse(open('/'.join(filepath)), format="trig")
        return nanopub
