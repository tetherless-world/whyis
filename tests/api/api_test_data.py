HOME_INSTANCE_URI = "http://localhost:5000/Home"

HOME_PAGE_CLASS_URI = "http://vocab.rpi.edu/whyis/HomePage"

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

