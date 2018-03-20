import autonomic
from rdflib import *
from slugify import slugify
import nanopub

sioc_types = Namespace("http://rdfs.org/sioc/types#")
sioc = Namespace("http://rdfs.org/sioc/ns#")
sio = Namespace("http://semanticscience.org/resource/")
dc = Namespace("http://purl.org/dc/terms/")
prov = autonomic.prov
whyis = autonomic.whyis

        
