HOME_INSTANCE_URI = "http://localhost:5000/Home"

HOME_PAGE_CLASS_URI = "http://vocab.rpi.edu/whyis/HomePage"

LOD_PREFIX = "http://localhost:5000"

ONTOLOGY_INSTANCE_URI = "http://example.com/janetology"

ONTOLOGY_INSTANCE_TURTLE = """\
<%(ONTOLOGY_INSTANCE_URI)s> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .""" % globals()

PERSON_CLASS_URI = "http://schema.org/Person"

PERSON_CLASS_TURTLE = """\
<%(PERSON_CLASS_URI)s> a <http://www.w3.org/2002/07/owl#Class> .""" % locals()

PERSON_INSTANCE_URI = "http://example.com/janedoe"

PERSON_INSTANCE_TURTLE = """\
<%(PERSON_INSTANCE_URI)s> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://purl.org/dc/terms/description> "Jane Doe is a person" ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .""" % globals()

PERSON_INSTANCE_BNODE_TURTLE = """\
<%(PERSON_INSTANCE_URI)s> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> [a <http://schema.org/URL>] ;
    <http://purl.org/dc/terms/description> "Jane Doe is a person" ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .""" % globals()


PERSON_INSTANCE_TRIG = """\
@prefix np: <http://www.nanopub.org/nschema#>.

_:nanopub {
  _:nanopub a np:Nanopublication;
    np:hasAssertion _:assertion;
    np:hasProvenance _:provenance;
    np:hasPublicationInfo _:pubinfo.
  _:assertion a np:Assertion.
  _:provenance a np:Provenance.
  _:pubinfo a np:PublicationInfo.
}

_:assertion {
<%(PERSON_INSTANCE_URI)s> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://purl.org/dc/terms/description> "Jane Doe is a person" ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
}
""" % globals()

