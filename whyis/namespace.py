import rdflib

auth = rdflib.Namespace("http://vocab.rpi.edu/auth/")
dc = rdflib.Namespace("http://purl.org/dc/terms/")
foaf = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
frbr = rdflib.Namespace("http://purl.org/vocab/frbr/core#")
np = rdflib.Namespace("http://www.nanopub.org/nschema#")
prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
pv = rdflib.Namespace("http://purl.org/net/provenance/ns#")
setl = rdflib.Namespace("http://purl.org/twc/vocab/setl/")
sio = rdflib.Namespace("http://semanticscience.org/resource/")
sioc = rdflib.Namespace("http://rdfs.org/sioc/ns#")
sioc_types = rdflib.Namespace("http://rdfs.org/sioc/types#")
skos = rdflib.Namespace("http://www.w3.org/2008/05/skos#")
whyis = rdflib.Namespace('http://vocab.rpi.edu/whyis/')
owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
text = rdflib.Namespace("http://jena.apache.org/fulltext#")


class NamespaceContainer(object):
    RDFS = rdflib.RDFS
    RDF = rdflib.RDF
    rdfs = rdflib.Namespace(rdflib.RDFS)
    rdf = rdflib.Namespace(rdflib.RDF)
    owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
    xsd = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")
    dc = rdflib.Namespace("http://purl.org/dc/terms/")
    dcterms = rdflib.Namespace("http://purl.org/dc/terms/")
    dcelements = rdflib.Namespace("http://purl.org/dc/elements/1.1/")
    auth = rdflib.Namespace("http://vocab.rpi.edu/auth/")
    foaf = rdflib.Namespace("http://xmlns.com/foaf/0.1/")
    prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
    skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    cmo = rdflib.Namespace("http://purl.org/twc/ontologies/cmo.owl#")
    sio = rdflib.Namespace("http://semanticscience.org/resource/")
    sioc_types = rdflib.Namespace("http://rdfs.org/sioc/types#")
    sioc = rdflib.Namespace("http://rdfs.org/sioc/ns#")
    np = rdflib.Namespace("http://www.nanopub.org/nschema#")
    whyis = rdflib.Namespace("http://vocab.rpi.edu/whyis/")
    ov = rdflib.Namespace("http://open.vocab.org/terms/")
    frbr = rdflib.Namespace("http://purl.org/vocab/frbr/core#")
    mediaTypes = rdflib.Namespace("https://www.iana.org/assignments/media-types/")
    pv = rdflib.Namespace("http://purl.org/net/provenance/ns#")
    sd = rdflib.Namespace('http://www.w3.org/ns/sparql-service-description#')
    ld = rdflib.Namespace('http://purl.org/linked-data/api/vocab#')
    dcat = rdflib.Namespace("http://www.w3.org/ns/dcat#")
    hint = rdflib.Namespace("http://www.bigdata.com/queryHints#")
    void = rdflib.Namespace("http://rdfs.org/ns/void#")
    schema = rdflib.Namespace("http://schema.org/")
    setl = rdflib.Namespace("http://purl.org/twc/vocab/setl/")
    sdd = rdflib.Namespace("http://purl.org/twc/sdd/")
    csvw = rdflib.Namespace("http://www.w3.org/ns/csvw#")
    text = rdflib.Namespace("http://jena.apache.org/fulltext#")

    @property
    def prefixes(self):
        result = {}
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, rdflib.Namespace):
                result[key] = value
        return result


NS = NamespaceContainer()
