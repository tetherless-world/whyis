from __future__ import print_function
from builtins import range
from builtins import object
import rdflib
import os
import collections
import requests
from dataurl import DataURLStorage
from werkzeug.utils import secure_filename

import tempfile

from depot.io.utils import FileIntent
from depot.manager import DepotManager

from datetime import datetime
import pytz

np = rdflib.Namespace("http://www.nanopub.org/nschema#")
prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
dc = rdflib.Namespace("http://purl.org/dc/terms/")
frbr = rdflib.Namespace("http://purl.org/vocab/frbr/core#")
from uuid import uuid4

from datastore import create_id

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


class NanopublicationManager(object):
    def __init__(self, store, prefix, app, update_listener=None):
        self.db = rdflib.ConjunctiveGraph(store)
        self.store = store
        self.app = app
        self.depot = DepotManager.get('nanopublications')
        self.prefix = rdflib.Namespace(prefix)
        self.update_listener = update_listener

    def new(self):
        fileid = self._reserve_id()
        nanopub = Nanopublication(identifier=self.prefix[fileid])
        nanopub.nanopub_resource
        nanopub.assertion
        nanopub.provenance
        nanopub.pubinfo

        return nanopub

    def _reserve_id(self):
        # This needs to be a two-step write, since we need to store
        # the identifier in the nanopub for consistency, and we don't
        # get the identifier until we write the file!
        fileid = self.depot.create(FileIntent(b'', create_id(), 'application/trig'))
        return fileid
                    
    def prepare(self, graph, mappings = None, store=None):
        if mappings is None:
            mappings = {}
        new_nps = list(graph.subjects(rdflib.RDF.type, np.Nanopublication))
        if len(new_nps) == 0:
            for context in list(graph.contexts()):
                new_np = Nanopublication(store=context.store)
                new_np.add((new_np.identifier, rdflib.RDF.type, np.Nanopublication))
                new_np.add((new_np.identifier, np.hasAssertion, context.identifier))
                new_np.add((graph.identifier, rdflib.RDF.type, np.Assertion))
                new_nps.append(new_np.identifier)
        for nanopub in new_nps:
            if self.prefix not in nanopub:
                fileid = self._reserve_id()
                new_uri = self.prefix[fileid]
                mappings[nanopub] = new_uri
                for assertion in graph.objects(nanopub, np.hasAssertion):
                    mappings[assertion] = rdflib.URIRef(new_uri+"_assertion")
                for pubinfo in graph.objects(nanopub, np.hasPublicationInfo):
                    mappings[pubinfo] = rdflib.URIRef(new_uri+"_pubinfo")
                for provenance in graph.objects(nanopub, np.hasProvenance):
                    mappings[provenance] = rdflib.URIRef(new_uri+"_provenance")
                
        #print mappings

        if store is None:
            output_graph = rdflib.ConjunctiveGraph()
        else:
            output_graph = rdflib.ConjunctiveGraph(store=store)

        bnode_cache = {}
        for s, p, o, g in graph.quads():
            def skolemize(x):
                if isinstance(x, rdflib.BNode):
                    if x not in bnode_cache:
                        bnode_cache[x] = rdflib.URIRef('bnode:'+uuid4().hex)
                    return bnode_cache[x]
                return x
            quad = (skolemize(mappings.get(s,s)), mappings.get(p,p), skolemize(mappings.get(o,o)), mappings.get(g.identifier,g.identifier))
            #print s, p, o, g
            #print quad
            output_graph.add(quad)

        i = 0
        for nanopub_uri in output_graph.subjects(rdflib.RDF.type, np.Nanopublication):
            i += 1
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
            if nanopub.pubinfo.value(nanopub.identifier, frbr.realizationOf) is None:
                work = self.prefix[create_id()]
                nanopub.pubinfo.add((nanopub.identifier, frbr.realizationOf, work))
                nanopub.pubinfo.add((work, rdflib.RDF.type, frbr.Work))
                nanopub.pubinfo.add((nanopub.identifier, rdflib.RDF.type, frbr.Expression))
            #print "Total", len(output_graph)
            #print "Contexts", [g.identifier for g in output_graph.contexts()]
            yield nanopub
            
    def retire(self, *nanopub_uris):
        self.db.store.nsBindings = {}
        graphs = []
        for nanopub_uri in nanopub_uris:
            for np_uri, assertion, provenance, pubinfo in self.db.query('''select ?np ?assertion ?provenance ?pubinfo where {
    hint:Query hint:optimizer "Runtime" .
    ?np (np:hasAssertion/prov:wasDerivedFrom+/^np:hasAssertion)? ?retiree.
    ?np np:hasAssertion ?assertion;
        np:hasPublicationInfo ?pubinfo;
        np:hasProvenance ?provenance.
}''', initNs={"prov":prov, "np":np}, initBindings={"retiree":nanopub_uri}):
                print("Retiring", np_uri, "derived from", nanopub_uri)
                graphs.extend([np_uri, assertion, provenance, pubinfo])
                nanopub = Nanopublication(store=self.db.store, identifier=np_uri)
                self.db.remove((None,None,None,nanopub.assertion.identifier))
                self.db.remove((None,None,None,nanopub.provenance.identifier))
                self.db.remove((None,None,None,nanopub.pubinfo.identifier))
                self.db.remove((None,None,None,nanopub.identifier))
        self.db.commit()
        #data = [('c', c.n3()) for c in graphs]
        #session = requests.session()
        #session.keep_alive = False
        #session.delete(self.db.store.endpoint, data=[('c', c.n3()) for c in graphs])
        print("Retired %s nanopubs." % len(nanopub_uris))

    def is_current(self, nanopub_uri):
        work = self.db.value(rdflib.URIRef(nanopub_uri), frbr.realizationOf)
        return work is not None
            
    def get_path(self, nanopub_uri):
        #print self.prefix, nanopub_uri
        ident = nanopub_uri.replace(self.prefix, "")
        dir_name_length = 3
        path = [ident[i:i+dir_name_length] for i in range(0, len(ident), dir_name_length)]
        return [self.archive_path] + path[:-1] + [ident]

    def _get_nanopubs(self, graph):
        for nanopub_uri in graph.subjects(rdflib.RDF.type, np.Nanopublication):
            i += 1
            nanopub = Nanopublication(identifier=nanopub_uri)
            nanopub += graph.get_context(nanopub.identifier)
            #print "Nanopub", len(nanopub), len(output_graph.get_context(identifier=nanopub_uri))
            for assertion in graph.objects(nanopub.identifier, np.hasAssertion):
                a = nanopub.assertion
                a += graph.get_context(identifier=assertion)
                #print "Assertion", len(a), len(output_graph.get_context(identifier=assertion))
            for pubinfo in output_graph.objects(nanopub.identifier, np.hasPublicationInfo):
                p = nanopub.pubinfo
                p += graph.get_context(identifier=pubinfo)
                #print "PubInfo", len(p), len(output_graph.get_context(identifier=pubinfo))
            for provenance in output_graph.objects(nanopub.identifier, np.hasProvenance):
                p = nanopub.provenance
                p += graph.get_context(identifier=provenance)
                #print "Provenance", len(p), len(output_graph.get_context(identifier=provenance))
            yield nanopub
        
    def publish(self, *nanopubs):
        #self.db.store.nsBindings = {}
        full_list = []
        with tempfile.NamedTemporaryFile(delete=False) as data:
            to_retire = []
            for np_graph in nanopubs:
                for entity in np_graph.subjects(self.app.NS.whyis.hasContent):
                    localpart = self.db.qname(entity).split(":")[1]
                    filename = secure_filename(localpart)
                    f = DataURLStorage(np_graph.value(entity, self.app.NS.whyis.hasContent), filename=filename)
                    print('adding file', filename)
                    self.app.add_file(f, entity, np_graph)
                    np_graph.remove((entity, self.app.NS.whyis.hasContent, None))
                
                
                for context in np_graph.contexts():
                    if (context.identifier,rdflib.RDF.type, np.Nanopublication) in context:
                        nanopub_uri = context.identifier
                    else:
                        continue
                    fileid = nanopub_uri.replace(self.prefix, "")
                    r = False
                    now = rdflib.Literal(datetime.utcnow())
                    nanopub = Nanopublication(identifier=nanopub_uri, store=np_graph.store)
                    for revised in nanopub.pubinfo.objects(nanopub.assertion.identifier, prov.wasRevisionOf):
                        for nanopub_uri in self.db.subjects(predicate=np.hasAssertion, object=revised):
                            nanopub.pubinfo.set((nanopub_uri, prov.invalidatedAtTime, now))
                            to_retire.append(nanopub_uri)
                            r = True
                            print("Retiring", nanopub_uri)
                    if r:
                        nanopub.pubinfo.set((nanopub.assertion.identifier, dc.modified, now))
                    else:
                        nanopub.pubinfo.set((nanopub.assertion.identifier, dc.created, now))
                    g = rdflib.ConjunctiveGraph()
                    for graph_part in [rdflib.Graph(identifier=x.identifier, store=x.store) for x in (nanopub, nanopub.assertion, nanopub.provenance, nanopub.pubinfo)]:
                        g_part = rdflib.Graph(identifier=graph_part.identifier, store=g.store)
                        for s,p,o in graph_part:
                            g_part.add((s,p,o))


                    serialized = g.serialize(format="trig")
                    self.depot.replace(fileid, FileIntent(serialized, fileid, 'application/trig'))
                    data.write(serialized)
                    data.write(b'\n')
                    data.flush()
                    full_list.append(nanopub.identifier)
                #np_graph.serialize(data, format="trig")
                #data.write('\n')
                #data.flush()
                #print data.name
                #np_graph.serialize(data, format="trig")
                #data.write('\n')
                #data.flush()
            self.retire(*to_retire)
            data.seek(0)
            self.db.store.publish(data, *nanopubs)
            print("Published %s nanopubs" % len(full_list))
            
        for n in full_list:
            self.update_listener(n)

    _idmap = {}
        
    def get(self, nanopub_uri, graph = None):
        nanopub_uri = rdflib.URIRef(nanopub_uri)
        f = None
        if nanopub_uri in self._idmap:
            f = self.depot.get(self._idmap[nanopub_uri])
        else:
            #try:
                fileid = nanopub_uri.replace(self.prefix, "", 1)
                f = self.depot.get(fileid)
            #except:
            #    try:
            #        fileid = self.db.value(nanopub_uri, dc.identifier)
            #        if fileid is not None:
            #            self._idmap[nanopub_uri] = fileid
            #        f = self.depot.get(fileid)
            #    except Exception as e:
            #        return None
        if graph is None:
            graph = rdflib.ConjunctiveGraph()
        nanopub = Nanopublication(store=graph.store, identifier=nanopub_uri)
        nanopub.parse(f, format="trig")
        try:
            f.close()
        except:
            pass
        return nanopub
