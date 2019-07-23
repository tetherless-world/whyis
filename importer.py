import requests
import rdflib
import nanopub
import datetime
import pytz
import dateutil.parser
from dateutil.tz import tzlocal
from werkzeug.datastructures import FileStorage
from werkzeug.http import http_date
from setlr import FileLikeFromIter
import re
import os
from requests_testadapter import Resp
import magic
import mimetypes
import traceback
import sys

from namespace import np, prov, dc, sio

invalid_escape = re.compile(r'\\[0-7]{1,3}')  # up to 3 digits for byte values up to FF

def replace_with_byte(match):
    return chr(int(match.group(0)[1:], 8))

def repair(brokenjson):
    return invalid_escape.sub(replace_with_byte, brokenjson.encode('utf8').replace(b'\u000','').decode('utf8'))

class Importer:

    min_modified = 0

    import_once=False

    @staticmethod
    def last_modified(entity_name, db, nanopubs):
        old_nps = [nanopubs.get(x) for x, in db.query('''select ?np where {
    ?np np:hasAssertion ?assertion.
    ?assertion a np:Assertion; prov:wasQuotedFrom ?mapped_uri.
}''',initNs=dict(np=np, prov=prov), initBindings=dict(mapped_uri=rdflib.URIRef(entity_name)))]
        modified = None
        for old_np in old_nps:
            m = old_np.modified
            if m is not None:
                m = m
                #m = pytz.utc.localize(m)
            if m is None:
                continue
            if modified is None or m > modified:
                print(m, modified, old_np.modified)
                modified = m
        return modified
        
    def load(self, entity_name, db, nanopubs):
        entity_name = rdflib.URIRef(entity_name)
        print("Fetching", entity_name)
        old_nps = [nanopubs.get(x) for x, in db.query('''select ?np where {
    ?np np:hasAssertion ?assertion.
    ?assertion a np:Assertion; prov:wasQuotedFrom ?mapped_uri.
}''',initNs=dict(np=np, prov=prov), initBindings=dict(mapped_uri=rdflib.URIRef(entity_name)))]
        updated = self.modified(entity_name)
        if updated is None:
            updated = datetime.datetime.now(pytz.utc)
        try:
            g = self.fetch(entity_name)
        except Exception as e:
            print("Error loading %s: %s" %(entity_name,e))
            traceback.print_exc(file=sys.stdout)
            return
        for new_np in nanopubs.prepare(g):
            print("Adding new nanopub:", new_np.identifier)
            self.explain(new_np, entity_name)
            new_np.add((new_np.identifier, sio.isAbout, entity_name))
            if updated is not None:
                new_np.pubinfo.add((new_np.assertion.identifier, dc.modified, rdflib.Literal(updated, datatype=rdflib.XSD.dateTime)))
            for old_np in old_nps:
                new_np.pubinfo.add((old_np.assertion.identifier, prov.invalidatedAtTime, rdflib.Literal(updated, datatype=rdflib.XSD.dateTime)))
            nanopubs.publish(new_np)

        for old_np in old_nps:
            print("retiring", old_np.identifier)
            nanopubs.retire(old_np.identifier)

    def explain(self, new_np, entity_name):
        activity = rdflib.BNode()
        new_np.provenance.add((activity, rdflib.RDF.type, self.app.NS.whyis.KnowledgeImport))
        new_np.provenance.add((new_np.assertion.identifier, prov.wasGeneratedBy, activity))
        new_np.provenance.add((activity, prov.used, rdflib.URIRef(entity_name)))
        new_np.provenance.add((new_np.assertion.identifier, prov.wasQuotedFrom, rdflib.URIRef(entity_name)))
        new_np.provenance.add((new_np.assertion.identifier, prov.wasDerivedFrom, rdflib.URIRef(entity_name)))
        

class LinkedData (Importer):
    def __init__(self, prefix, url, headers=None, access_url=None,
                 format=None, modified_headers=None, postprocess_update=None,
                 postprocess=None, min_modified=0, import_once=False):
        self.prefix = prefix
        self.url = url
        self.detect_url = url.split("%s")[0]
        self.headers = headers
        self.modified_headers = modified_headers
        self.format = format
        self.min_modified = min_modified
        self.import_once = import_once
        if access_url is not None:
            self.access_url = access_url
        else:
            self.access_url = "%s"
        if callable(self.access_url):
            self._get_access_url = self.access_url
        else:
            self._get_access_url = lambda entity_name: self.access_url % entity_name
        self.postprocess_update = postprocess_update
        self.postprocess = postprocess

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
        u = self._get_access_url(entity_name)
        print("accessing at", u)
        requests_session = requests.session()
        requests_session.mount('file://', LocalFileAdapter())
        requests_session.mount('file:///', LocalFileAdapter())
        r = requests_session.head(u, headers=self.modified_headers, allow_redirects=True)
        #print "Modified Headers", r.headers
        if 'Last-Modified' in r.headers:
            result = dateutil.parser.parse(r.headers['Last-Modified'])
            #print result, r.headers['Last-Modified']
            return result

        return None


    def fetch(self, entity_name):
        u = self._get_access_url(entity_name)
        print(u)
        r = requests.get(u, headers = self.headers, allow_redirects=True)
        g = rdflib.Dataset()
        local = g.graph(rdflib.URIRef("urn:default_assertion"))
        local.parse(data=r.text, format=self.format)
        #print self.postprocess_update
        if self.postprocess_update is not None:
            #print "update postprocess query."
            g.update(self.postprocess_update)
        if self.postprocess is not None:
            print("postprocessing", entity_name)
            p = self.postprocess
            p(g)
        #print g.serialize(format="trig")
        return rdflib.ConjunctiveGraph(identifier=local.identifier, store=g.store)
        
        
class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        mtime = os.path.getmtime(file_path)
        dt = datetime.datetime.fromtimestamp(mtime, tzlocal())
        mimetype = mimetypes.guess_type(file_path)[0]
        if mimetype is None:
            mimetype = magic.from_file(file_path, mime=True)
        headers = {"Last-Modified": http_date(dt)}
        if mimetype is not None:
            headers['Content-Type'] = mimetype
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff, headers=headers)
            r = self.build_response(request, resp)
            return r
    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):
        return self.build_response_from_file(request)

class FileImporter (LinkedData):

    def __init__(self, prefix, url, file_types=None, **kwargs):
        LinkedData.__init__(self, prefix, url, **kwargs)
        self.file_types = file_types
    
    def fetch(self, entity_name):
        u = self._get_access_url(entity_name)
        requests_session = requests.session()
        requests_session.mount('file://', LocalFileAdapter())
        requests_session.mount('file:///', LocalFileAdapter())
        r = requests_session.get(u, headers = self.headers, allow_redirects=True, stream=True)
        npub = nanopub.Nanopublication()
        if 'content-disposition' in r.headers:
            d = r.headers['content-disposition']
            fname = re.findall("filename=(.+)", d)
        else:
            fname = entity_name.split('/')[-1]
        content_type = r.headers.get('content-type')

        if self.file_types is not None:
            for file_type in self.file_types:
                npub.assertion.add((entity_name, rdflib.RDF.type, file_type))
        f = FileStorage(FileLikeFromIter(r.iter_content()), fname, content_type=content_type)
        old_nanopubs = self.app.add_file(f, entity_name, npub)
        npub.assertion.add((entity_name, self.app.NS.RDF.type, self.app.NS.pv.File))
        
        # old_np variable unused
        for _, old_np_assertion in old_nanopubs:
            npub.pubinfo.add((npub.assertion.identifier, self.app.NS.prov.wasRevisionOf, old_np_assertion))

        return npub
