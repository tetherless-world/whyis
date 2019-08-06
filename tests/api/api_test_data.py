ONTOLOGY_INSTANCE_TURTLE = """\
<http://example.com/> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
<http://schema.org/name> "Jane Doe" ;
<http://schema.org/telephone> "(425) 123-4567" ;
<http://schema.org/url> <http://www.janedoe.com> ;
<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> ."""

PERSON_INSTANCE_TURTLE = """\
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> ."""
