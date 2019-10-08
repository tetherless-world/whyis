import rdflib
import owlrl
import time
import autonomic
from rdflib import *
from slugify import slugify
from nanopub import Nanopublication
from flask_script import Command, Option
import flask

class RLReasoner(Command):

    def get_options(self):
        return [
            Option('--closure', '-c', dest='closure_bool', type=bool),
            Option('--axiomatic', '-a', dest='axiomatic_bool', type=bool),
            Option('--datatype_axiom', '-d', dest='datatype_axiom_bool', type=bool)
        ]

    def run(self, closure_bool = False, axiomatic_bool = False, datatype_axiom_bool = False):
        app = flask.current_app # set app to be current flask app 
        new_graph = rdflib.ConjunctiveGraph() # create new empty graph to run reasoner
        new_graph += app.db # add current graph to new graph
        owlrl.DeductiveClosure(owlrl.OWLRL_Extension, rdfs_closure = closure_bool, axiomatic_triples = axiomatic_bool, datatype_axioms = datatype_axiom_bool).expand(new_graph) # run reasoner using specified options
        new_graph -= app.db # remove content from initial graph from the new graph
        # output graph (for testing purposes mostly)
        new_graph.serialize("inferred_graph.ttl", format="turtle")

        # append inferred graph to knowledge base
        npub = Nanopublication(store=app.db.store)
        q = "SELECT DISTINCT ?s ?p ?o WHERE {?s ?p ?o .}"
        triples = new_graph.query(q)
        for triple in list(triples):#new_graph.triples((None,None,None)):
            try:
                npub.assertion.add((triple[0],triple[1],triple[2]))
                print("Added:", triple)
            except Exception as e:
                continue
#                if hasattr(e, 'message'):
#                    print("Error: Unable to add: ", triple, "\n", e.message)
#                else:
#                    print("Error: Unable to add: ", triple, "\n", e)
                
