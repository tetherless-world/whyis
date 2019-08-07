HOME_INSTANCE_URI = "http://localhost:5000/Home"

PERSON_INSTANCE_URI = "http://example.com/janedoe"

PERSON_INSTANCE_TURTLE = """\
<%(PERSON_INSTANCE_URI)s> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .""" % globals()

