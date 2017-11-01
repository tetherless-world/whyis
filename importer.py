import requests
import rdflib
import nanopub
import datetime
import email.utils as eut
import pytz
import dateutil.parser

np = rdflib.Namespace('http://www.nanopub.org/nschema#')
prov = rdflib.Namespace('http://www.w3.org/ns/prov#')
dc = rdflib.Namespace('http://purl.org/dc/terms/')
sio = rdflib.Namespace('http://semanticscience.org/resource/')

import re
invalid_escape = re.compile(r'\\[0-7]{1,3}')  # up to 3 digits for byte values up to FF

def replace_with_byte(match):
    return chr(int(match.group(0)[1:], 8))

def repair(brokenjson):
    return invalid_escape.sub(replace_with_byte, brokenjson.replace('\u000',''))

class Importer:

    min_modified = 0
    
    def last_modified(self, entity_name, db, nanopubs):
        old_nps = [nanopubs.get(x) for x, in db.query('''select ?np where {
    ?np np:hasAssertion ?assertion.
    ?assertion a np:Assertion; prov:wasQuotedFrom ?mapped_uri.
}''',initNs=dict(np=np, prov=prov), initBindings=dict(mapped_uri=rdflib.URIRef(entity_name)))]
        modified = None
        for old_np in old_nps:
            m = old_np.modified
            if m is not None:
                m = m
                m = pytz.utc.localize(m)
            if m is None:
                continue
            if modified is None or m > modified:
                print m, modified, old_np.modified
                modified = m
        return modified
        
    def load(self, entity_name, db, nanopubs):
        print "Fetching", entity_name
        old_nps = [nanopubs.get(x) for x, in db.query('''select ?np where {
    ?np np:hasAssertion ?assertion.
    ?assertion a np:Assertion; prov:wasQuotedFrom ?mapped_uri.
}''',initNs=dict(np=np, prov=prov), initBindings=dict(mapped_uri=rdflib.URIRef(entity_name)))]
        updated = self.modified(entity_name)
        if updated is None:
            updated = datetime.datetime.now(pytz.utc)
        g = self.fetch(entity_name)
        for new_np in nanopubs.prepare(g):
            #print "Adding new nanopub:", new_np.identifier
            self.explain(new_np, entity_name)
            new_np.add((new_np.identifier, sio.isAbout, rdflib.URIRef(entity_name)))
            if updated != None:
                new_np.pubinfo.add((new_np.assertion.identifier, dc.modified, rdflib.Literal(updated, datatype=rdflib.XSD.dateTime)))
            for old_np in old_nps:
                new_np.pubinfo.add((old_np.assertion.identifier, prov.invalidatedAtTime, rdflib.Literal(updated, datatype=rdflib.XSD.dateTime)))
            #print new_np.serialize(format="trig")
            nanopubs.publish(new_np)

        for old_np in old_nps:
            print "retiring", old_np.identifier
            nanopubs.retire(old_np.identifier)

    def explain(self, new_np, entity_name):
        new_np.provenance.add((new_np.assertion.identifier, prov.wasQuotedFrom, rdflib.URIRef(entity_name)))
        

class LinkedData (Importer):
    def __init__(self, prefix, url, headers=None, access_url=None, format=None, modified_headers=None, postprocess_update=None, min_modified=0):
        self.prefix = prefix
        self.url = url
        self.detect_url = url.split("%s")[0]
        self.headers = headers
        self.modified_headers = modified_headers
        self.format = format
        self.min_modified = min_modified
        if access_url is not None:
            self.access_url = access_url
        else:
            self.access_url = "%s"
        self.postprocess_update = postprocess_update

    def resource_matches(self, entity):
        return entity.startswith(self.detect_url)
        
    def matches(self, entity_name):
        #print entity_name, self.prefix, entity_name.startswith(self.prefix)
        return entity_name.startswith(self.prefix)

    def map(self, entity_name):
        fragment = self.get_fragment(entity_name)
        return rdflib.URIRef(self.url % fragment)

    def get_fragment(self, entity_name):
        fragment = entity_name[len(self.prefix):]
        return fragment

    def modified(self, entity_name):
        u = self.access_url % entity_name
        r = requests.head(u, headers=self.modified_headers, allow_redirects=True)
        #print "Modified Headers", r.headers
        if 'Last-Modified' in r.headers:
            result = dateutil.parser.parse(r.headers['Last-Modified'])
            #print result, r.headers['Last-Modified']
            return result
        else:
            return None


    def fetch(self, entity_name):
        u = self.access_url % entity_name
        #print u
        r = requests.get(u, headers = self.headers)
        g = rdflib.Dataset()
        local = g.graph(rdflib.URIRef("urn:default_assertion"))
        local.parse(data=repair(r.text), format=self.format)
        #print self.postprocess_update
        if self.postprocess_update is not None:
            #print "update postprocess query."
            g.update(self.postprocess_update)
        #print g.serialize(format="trig")
        return rdflib.ConjunctiveGraph(identifier=local.identifier, store=g.store)
        
        
