from rdflib import RDF
from rdflib.graph import ConjunctiveGraph
from rdflib.resource import Resource


class MappedResource(Resource):

    rdf_type = None
    key = None

    def __init__(self, graph=None, subject=None, **kwargs):

        if subject is None and self.key in kwargs:
            subject = self.prefix[kwargs[self.key]]

        if graph is None:
            graph = ConjunctiveGraph(identifier=subject)
            
        Resource.__init__(self,graph, subject)

        if self.rdf_type and not self[RDF.type:self.rdf_type]:
            self.graph.add((self.identifier, RDF.type, self.rdf_type))
            
        if kwargs:
            self._set_with_dict(kwargs)

    def _set_with_dict(self, kv):
        """
        :param kv: a dict

          for each key,value pair in dict kv
               set self.key = value

        """
        for key, value in list(kv.items()):
            descriptor = self.__class__._getdescriptor(key)
            descriptor.__set__(self, value)
            
    @classmethod
    def _getdescriptor(cls, key):
        """__get_descriptor returns the descriptor for the key.
        It essentially cls.__dict__[key] with recursive calls to super"""
        # NOT SURE if mro is the way to do this or if we should call super or bases?
        for kls in cls.mro():
            if key in kls.__dict__:
                return kls.__dict__[key]
        raise AttributeError("descriptor %s not found for class %s" % (key,cls))

#    def __str__(self):
#        return type(self).__name__ + ' ' + super().__str__() + ' a ' + self.rdf_type

