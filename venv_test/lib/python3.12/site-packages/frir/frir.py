#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import hex
from builtins import map
from builtins import str
from builtins import object
from rdflib import *

import re, os, sys
from stat import *

import rdflib
import rdflib.term
import hashlib
import http.client
from urllib.parse import urlparse, urlunparse
import dateutil.parser
from datetime import datetime

import subprocess
import platform
from base64 import *
import base64

import uuid

from sadi.serializers import *

from io import StringIO

import fileinput
import binascii

from sadi import OntClass, contentTypes

def bindPrefixes(graph):
    graph.bind('frbr', URIRef('http://purl.org/vocab/frbr/core#'))
    graph.bind('frir', URIRef('http://purl.org/twc/ontology/frir.owl#'))
    graph.bind('pexp', URIRef('tag:tw.rpi.edu,2011:Expression:'))
    graph.bind('pmanif', URIRef('tag:tw.rpi.edu,2011:Manifestation:'))
    graph.bind('pitem', URIRef('tag:tw.rpi.edu,2011:Item:'))
    graph.bind('nfo', URIRef('http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#'))
    graph.bind('irw', URIRef('http://www.ontologydesignpatterns.org/ont/web/irw.owl#'))
    graph.bind('dc', URIRef('http://purl.org/dc/terms/'))
    graph.bind('prov', URIRef('http://dvcs.w3.org/hg/prov/raw-file/tip/ontology/ProvenanceOntology.owl#'))
    graph.bind('xsd', URIRef('http://www.w3.org/2001/XMLSchema#'))
    graph.bind('http', URIRef("http://www.w3.org/2011/http#"))
    graph.bind('header', URIRef("http://www.w3.org/2011/http-headers#"))
    graph.bind('method', URIRef("http://www.w3.org/2011/http-methods#"))
    graph.bind('status', URIRef("http://www.w3.org/2011/http-statusCodes#"))

def packl(lnum, padmultiple=1):
    """Packs the lnum (which must be convertable to a long) into a
       byte string 0 padded to a multiple of padmultiple bytes in size. 0
       means no padding whatsoever, so that packing 0 result in an empty
       string.  The resulting byte string is the big-endian two's
       complement representation of the passed in long."""

    if lnum == 0:
        return b'\0' * padmultiple
    elif lnum < 0:
        raise ValueError("Can only convert non-negative numbers.")
    s = hex(lnum)[2:]
    s = s.rstrip('L')
    if len(s) & 1:
        s = '0' + s
    s = binascii.unhexlify(s)
    if (padmultiple != 1) and (padmultiple != 0):
        filled_so_far = len(s) % padmultiple
        if filled_so_far != 0:
            s = b'\0' * (padmultiple - filled_so_far) + s
    return s

serializers = {Literal:lambda x: '"'+x+'"@'+str(x.language)+'^^'+str(x.datatype),
               URIRef:lambda x: '<'+str(x)+'>',
               BNode:lambda x: '['+str(x)+']'}

frbr = Namespace("http://purl.org/vocab/frbr/core#")
frir = Namespace("http://purl.org/twc/ontology/frir.owl#")
nfo = Namespace("http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#")
irw = Namespace('http://www.ontologydesignpatterns.org/ont/web/irw.owl#')
hsh = Namespace("ni:///")
uuid = Namespace("uuid:")
void = Namespace("http://rdfs.org/ns/void#")
ov = Namespace("http://open.vocab.org/terms/")
dcterms = Namespace("http://purl.org/rc/terms/")
nie = Namespace("http://www.semanticdesktop.org/ontologies/2007/01/19/nie#")

def hash_tuple(t):
    def stringify(x):
        if isinstance(x,rdflib.term.Node):
            return x.n3()
        else: return str(x)
    def hfn(s):
        m = hashlib.sha256()
        m.update(' '.join([stringify(x) for x in t]).encode('utf-8'))
        return int(m.hexdigest(),16)
    print(t)
    return sum(map(hfn, t))
    #return sum([hfn(' '.join([stringify(x) for x in triple])) for triple in t])

def hash_triple(t):
    s = ' '.join([x.n3() for x in t])
    m = hashlib.sha256()
    m.update(s.encode('utf-8'))
    return int(m.hexdigest(),16)

def _hetero_tuple_key(x):
    "Sort like Python 2 - by name of type, then by value. Expects tuples."
    return tuple((type(a).__name__, a) for a in x)

class RDFGraphDigest(object):

    def __init__(self,prefix="tag:tw.rpi.edu,2011:"):
        print('0', self)
        self.pwork = Namespace(prefix+"work_")
        self.pexp = Namespace(prefix+"expression_")
        self.pmanif = Namespace(prefix+"manifestation_")
        self.pitem = Namespace(prefix+"item_")

        self.rawAllowedProps = set([
            dcterms.isReferencedBy,
            void.inDataset,
            RDFS.label,
            RDF.type,
            RDFS.range,
            ov.csvCol,
            ov.csvHeader,
            ov.csvRow
            ])

        self.rawRequiredColAnnotations = set([
            ov.csvCol,
            ov.csvHeader,
            ])

        self.rawRequiredRowAnnotations = set([
            ov.csvRow
            ])

        self.csvCol = ov.csvCol
        self.csvHeader = ov.csvHeader
        self.csvRow = ov.csvRow

        self.total = 0
        self.rawtotal = 0
        self.isRaw = True
        self.algorithm = 'graph-sha-256'
        self.type = frir.RDFGraphDigest

    def hashPredicates(self, graph):
        predicates = graph.predicates()
        result = set([])
        row = URIRef("row:1")
        for p in predicates:
            if p in self.rawAllowedProps:
                continue
            a = set(graph.predicates(subject=p))
            if a >= self.rawRequiredColAnnotations and a <= self.rawAllowedProps:
                col = URIRef("column:"+str(graph.value(p,self.csvCol)))
                value = graph.value(p, self.csvHeader)
                self.updateStatement((row,col,value),'raw')
                result.add(p)
            else:
                self.isRaw = False
                return None
        return result

    def hashSubjects(self, graph, predicates):
        predicates = graph.predicates()
        triples = set([])
        for stmt in graph:
            if stmt[1] in self.rawAllowedProps or stmt[0] in self.rawAllowedProps:
                continue
            if stmt[1] in predicates:
                row = graph.value(stmt[0],self.csvRow)
                if row == None:
                    self.isRaw = False
                    return
                row = URIRef("row:"+str(row))
                col = URIRef("column:"+str(graph.value(stmt[1],self.csvCol)))
                value = stmt[2]
                self.updateStatement((row,col,value), 'raw')
            else:
                self.isRaw = False
                return


    def loadAndUpdate(self,content, filename = None, mimetype = None):
        graph = Graph()
        try:
            t = deserialize(graph, content, mimetype)
            if t != None:
                self.type = t
        except Exception as e:
            try:
                if filename != None:
                    extension = filename.split('.')[-1]
                    mimetype = extensions[extension]
                    print("Using Extension", extension, mimetype)
                    serializer = contentTypes[extensions[extension]]
                    t = serializer.deserialize(graph, content, mimetype)
                    if len(graph) == 0:
                        raise Exception()
                    if t != None:
                        self.type = t
            except Exception as e2:
                print("Using Manifestation", e2)
                manifHash =  self.createManifestationHash(content)
                mimetype = None
                self.algorithm = manifHash[0]
                self.total = manifHash[1]
                self.type = manifHash[2]
                self.isRaw = False
                return
        self.update(graph)
        return mimetype

    def update(self, graph):
        graph = self.canonicalize(graph)
        print(graph.serialize(format="turtle"))
        self.triples = set([])
        if self.isRaw:
            predicates = self.hashPredicates(graph)
            if self.isRaw:
                self.hashSubjects(graph,predicates)
                if self.isRaw:
                    return
        for stmt in graph:
            self.updateStatement(stmt)

    def updateStatement(self, stmt, hashType="graph"):
        print(stmt)
        stmtDigest = hash_triple(stmt)
        #if stmtDigest in self.triples:
        #    return
        self.triples.add(stmtDigest)
        if hashType == 'graph':
            self.total += stmtDigest
            #print "total", self.total
        else:
            self.rawtotal += stmtDigest
            #print "raw total", stmtDigest

    class _TripleCanonicalizer(object):

        def __init__(self, graph, hashfunc=hash_tuple):
            self.graph = graph
            self.hashfunc = hashfunc
            self.bnodes = collections.defaultdict(list)
            self.new_bnodes = {}

        def to_hash(self):
            return self.hashfunc(tuple(sorted(
                map(self.hashfunc, self.canonical_triples()))))

        def canonical_triples(self):
            for triple in self.graph:
                yield tuple([self._canonicalize_bnodes(term) for term in triple])

        def _canonicalize_bnodes(self, term):
            if isinstance(term, BNode):
                if term in self.new_bnodes:
                    return self.new_bnodes[term]
                bnodeid = self._canonicalize(term)
                if bnodeid in self.bnodes:
                    bnid = str(bnodeid)+str(len(self.bnodes[bnodeid]))
                else: bnid = bnodeid
                self.bnodes[bnodeid].append(term)
                new_term = BNode(value="cb%s" % bnid)
                print("cb%s" % bnid)
                self.new_bnodes[term] = new_term
                return new_term
            else:
                return term

        def _canonicalize(self, term, done=False):
            return self.hashfunc(tuple(sorted(self._vhashtriples(term, done),
                                              key=_hetero_tuple_key)))

        def _vhashtriples(self, term, done):
            for triple in self.graph:
                if term in triple:
                    yield tuple(self._vhashtriple(triple, term, done))

        def _vhashtriple(self, triple, target_term, done):
            for i, term in enumerate(triple):
                if not isinstance(term, BNode):
                    yield term
                elif done or (term == target_term):
                    yield i
                else:
                    yield self._canonicalize(term, done=True)

    def canonicalize(self, g1):
        g2 = set(g1)
        g1 = Graph()
        g1 += g2
        print(g1.serialize(format="turtle"))
        graph = Graph()
        graph += self._TripleCanonicalizer(g2, hash_tuple).canonical_triples()
        return graph

    def getDigest(self):
        if self.isRaw:
            return [self.algorithm,
                    base64.urlsafe_b64encode(buffer(packl(self.rawtotal))),
                    frir.TabularDigest]
        else:
            value = self.total
            if type(value) == int:
                value = base64.urlsafe_b64encode(buffer(packl(value)))
            return [self.algorithm,
                    value,
                    self.type]

    def fstack(self, fd, filename=None, workuri=None, graph = None, mimetype=None, addPaths=True):
        if workuri != None: 
            workuri = URIRef(workuri)

        if graph == None:
            graph = Graph()

        print(dir(frir))
        Thing = OntClass(graph,OWL['Thing'])
        ContentDigest = OntClass(graph,frir.ContentDigest)
        Item = OntClass(graph,frbr.Item)
        Manifestation = OntClass(graph,frbr.Manifestation)
        Expression = OntClass(graph,frbr.Expression)
        Work = OntClass(graph,frbr.Work)

        fileURI = None
        if filename != None:
            fileURI = createItemURI(filename)

        content = fd.read()
    
        manifestationHashValue = self.createManifestationHash(content)

        print(self)
        if fileURI == None:
            fileURI = self.pitem['-'.join(manifestationHashValue[:2])]

        timestamp = datetime.utcnow()

        itemHashValue = manifestationHashValue
        item = Item(fileURI)
        item.add(nfo.hasHash,self.createHashInstance(itemHashValue,Thing))
        if addPaths and filename != None:
            item.add(nfo.fileUrl,URIRef('file:///'+os.path.abspath(filename)))
            item.add(nfo.fileUrl,URIRef(filename))
        if filename != None:
            item.add(dcterms.modified, Literal(datetime.fromtimestamp(os.stat(filename)[ST_MTIME])))
        item.add(dcterms.date, Literal(timestamp))

        manifestation = Manifestation(self.pmanif['-'.join(manifestationHashValue[:-1])])
        manifestation.add(nfo.hasHash,self.createHashInstance(manifestationHashValue,Thing))
        
        item.add(frbr.exemplarOf,manifestation)

        if filename == None and workuri != None:
            expressionHashValue, mimetype = self.createExpressionHash(workuri.split("/")[-1],content,mimetype)
        else:
            expressionHashValue, mimetype = self.createExpressionHash(filename, content, mimetype)
        expression = Expression(self.pexp['-'.join([str(x) for x in expressionHashValue[:-1]])])
        expression.add(frir.hasContentDigest,self.createHashInstance(expressionHashValue,ContentDigest))

        manifestation.add(frbr.embodimentOf,expression)
        manifestation.add(nie.mimeType,Literal(mimetype))
        if workuri != None:
            work = Work(workuri)
        else:
            work = Work(self.pwork['-'.join([str(x) for x in expressionHashValue[:-1]])])

        expression.add(frbr.realizationOf,work)

        return graph, item

    def createItemHash(self, workURI, response, content):
        m = hashlib.sha256()
        m.update(workURI+'\n')
        m.update(''.join(response.msg.headers))
        m.update(content)
        return ['sha-256',urlsafe_b64encode(buffer(m.digest())), nfo.FileHash]

    def createManifestationHash(self, content):
        m = hashlib.sha256()
        m.update(content)
        return ['sha-256',urlsafe_b64encode(buffer(m.digest())), nfo.FileHash]

    def createExpressionHash(self, filename, content, mimetype=None):
        mimetype = self.loadAndUpdate(content,filename,mimetype)
        return self.getDigest(), mimetype

    def createHashInstance(self, h, Hash):
        hs = Hash(hsh[';'.join([str(x) for x in h[:-1]])])
        hs.add(nfo.hashAlgorithm,Literal(h[0]))
        hs.add(nfo.hashValue,Literal(h[1]))
        if len(h) > 2:
            hs.add(RDF.type,h[2])
        return hs


    def createItemURI(self, filename,prefix="tag:tw.rpi.edu,2011:filed:"):
        m = hashlib.sha256()
        m.update(str(uuid.getnode()))
        m.update(str(os.stat(filename)[ST_MTIME]))
        hostAndModTime = urlsafe_b64encode(buffer(m.digest()))
        absolutePath = os.path.abspath(filename)
        dirname = os.path.dirname(absolutePath)
        basename = os.path.basename(absolutePath)
        m = hashlib.sha256()
        m.update(dirname)
        pathDigest = '-'.join(['sha-256',urlsafe_b64encode(buffer(m.digest()))])
        return prefix+hostAndModTime+'/'+pathDigest+'/'+basename

extensions = {
    "owl":"application/rdf+xml",
    "rdf":"application/rdf+xml",
    "ttl":"text/turtle",
    "n3":"text/n3",
    "ntp":"text/plain",
    'csv':'text/csv',
    'tsv':'text/tab-separated-values',
    "html":"text/html"
    }

typeExtensions = {
    "xml":'rdf',
    "turtle":'ttl',
    "n3":"n3",
    "nt":"ntp"
    }

def getFormat(contentType):
    if contentType == None: return [ "application/rdf+xml",serializeXML]
    type = mimeparse.best_match([x for x in list(contentTypes.keys()) if x != None],contentType)
    if type != None: return [type,contentTypes[type]]
    else: return [ "application/rdf+xml",serializeXML]

def serialize(graph, accept):
    format = getFormat(accept)
    return format[0],format[1].serialize(graph)

def deserialize(graph, content, mimetype):
    format = getFormat(mimetype)
    #print 'Foo'
    #print format
    format[1].deserialize(graph,content, mimetype)


def usage():
    print('''usage: fstack.py [--help|-h] [--stdout|-c] [--format|-f xml|turtle|n3|nt] [--print-item] [--print-manifesation] [--print-expression] [--print-work] [-] [file ...]

Compute Functional Requirements for Bibliographic Resources (FRBR)
stacks using cryptograhic digests.

Refer to http://purl.org/twc/pub/mccusker2012parallel
for more information and examples.

optional arguments:
 file                  File to compute a FRBR stack for.
 -                     Read content from stdin and print FRBR stack to stdout.
 -h, --help            Show this help message and exit,
 -c, --stdout          Print frbr stacks to stdout.
 --no-paths            Only output path hashes, not actual paths.
 -f, --format          File format for FRBR stacks. xml, turtle, n3, or nt.
--print-item           Print URI of the Item and quit.
--print-manifestation  Print URI of the Manifestation and quit.
--print-expression     Print URI of the Expression and quit.
--print-work           Print URI of the Work and quit.
''')

if __name__ == "__main__":
    files = set([])
    i = 1
    stdout = False
    fileFormat = 'turtle'
    extension = 'ttl'
    addPaths = True
    printItems = False
    printManifestations = False
    printExpressions = False
    printWorks = False

    if '-h' in sys.argv or '--help' in sys.argv:
        usage()
        quit()
    while i < len(sys.argv):
        if sys.argv[i] == '-c' or sys.argv[i] == '--stdout':
            stdout = True
        elif sys.argv[i] == '-f' or sys.argv[i] == '--format':
            fileFormat = sys.argv[i+1]
            try:
                extension = typeExtensions[fileFormat]
            except:
                usage()
                quit(1)
            i += 1
        elif sys.argv[i] == '--no-paths':
            addPaths = False
        elif sys.argv[i] == '--print-item':
            printItems = True
        elif sys.argv[i] == '--print-manifestation':
            printManifestations = True
        elif sys.argv[i] == '--print-expression':
            printExpressions = True
        elif sys.argv[i] == '--print-work':
            printWorks = True
        else:
            files.add(sys.argv[i])

        i += 1

    if len(files) == 0:
        files.add('-')
        
    for f in files:
        graph = None
        if f == '-':
            d = RDFGraphDigest()
            graph = d.fstack(sys.stdin,addPaths=addPaths)
            bindPrefixes(graph)
            # if printItems or printManifestations or printExpressions or printWorks:
            #     session = Session(store[0])
            #     if printItems:
            #         Item = session.get_class(ns.FRBR['Item'])
            #         for i in Item.all():
            #             print i.subject
            #     if printManifestations:
            #         Manifestation = session.get_class(ns.FRBR['Manifestation'])
            #         for i in Manifestation.all():
            #             print i.subject
            #     if printExpressions:
            #         Expression = session.get_class(ns.FRBR['Expression'])
            #         for i in Expression.all():
            #             print i.subject
            #     if printWorks:
            #         Work = session.get_class(ns.FRBR['Work'])
            #         for i in Work.all():
            #             print i.subject
            # else:
            print(graph.serialize(format=fileFormat))
        else:
            graph = fstack(open(f,'rb+'),f,addPaths=addPaths)
            bindPrefixes(graph)
            # if printItems or printManifestations or printExpressions or printWorks:
            #     session = Session(store[0])
            #     if printItems:
            #         Item = session.get_class(ns.FRBR['Item'])
            #         for i in Item.all():
            #             print i.subject
            #     if printManifestations:
            #         Manifestation = session.get_class(ns.FRBR['Manifestation'])
            #         for i in Manifestation.all():
            #             print i.subject
            #     if printExpressions:
            #         Expression = session.get_class(ns.FRBR['Expression'])
            #         for i in Expression.all():
            #             print i.subject
            #     if printWorks:
            #         Work = session.get_class(ns.FRBR['Work'])
            #         for i in Work.all():
            #             print i.subject
            # else:
            if stdout:
                print(graph.serialize(format=fileFormat))
            else:
                graph.serialize(open(f+".prov."+extension,'wb+'),format=fileFormat)
