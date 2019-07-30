from flask_security import RoleMixin
from whyis.namespace import prov
from rdflib import RDFS

from .single import single
from .mapped_resource import MappedResource

###  http://www.w3.org/ns/prov#Role
class Role(MappedResource, RoleMixin):
    rdf_type = prov.Role
    name = single(RDFS.label)
    key = 'name'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
