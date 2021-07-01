from flask import url_for, current_app
from flask_script import Command, Option
import urllib.request, urllib.parse, urllib.error


class RunAbductor(Command):
    """Display all valid routes in the application"""
    def get_options(self):
        return [
            Option('--input', '-i', dest='reasoning_dict', required=True,
                   type=str),
        ]

    def run(self, reasoning_dict):
        print(current_app.config)
        if "active_profiles" and "reasoning_profiles" in current_app.config :
            for profile in current_app.config["active_profiles"] :
                for rule_reference in current_app.config["reasoning_profiles"][profile] :
                    print(rule_reference)
                    for rule in current_app.config[reasoning_dict] :
                        if current_app.config[reasoning_dict][rule]["reference"] == rule_reference :
                            #triples = current_app.db.query('''CONSTRUCT { %s } WHERE { %s } ''' % ( current_app.config[reasoning_dict][rule]["consequent"], current_app.config[reasoning_dict][rule]["antecedent"]), initNs=current_app.config[reasoning_dict][rule]["prefixes"] )
                            print(current_app.config[reasoning_dict][rule]["rule"], current_app.config[reasoning_dict][rule]["reference"], current_app.config[reasoning_dict][rule]["antecedent"], current_app.config[reasoning_dict][rule]["consequent"], current_app.config[reasoning_dict][rule]["rule"], current_app.config[reasoning_dict][rule]["reference"], current_app.config[reasoning_dict][rule]["prefixes"])
                            triples = current_app.db.query('''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sets: <http://purl.org/ontology/sets/ont#>
CONSTRUCT {
    ?g2 sets:hypothesis
        [ a sets:Hypothesis , %s ; 
            rdfs:label "%s" ; 
            sets:antecedentGraph ?g1 
        ]  .
} WHERE {
    GRAPH ?g1 { %s }
    GRAPH ?g2 { %s }
    FILTER NOT EXISTS {
        ?g2 sets:hypothesis 
            [ a sets:Hypothesis , %s ; 
                rdfs:label "%s" ; 
                sets:antecedentGraph ?g1 
            ] .
    }
}''' % ( current_app.config[reasoning_dict][rule]["rule"], current_app.config[reasoning_dict][rule]["reference"], current_app.config[reasoning_dict][rule]["antecedent"], current_app.config[reasoning_dict][rule]["consequent"], current_app.config[reasoning_dict][rule]["rule"], current_app.config[reasoning_dict][rule]["reference"]), initNs=current_app.config[reasoning_dict][rule]["prefixes"] )
                            for s, p, o, c in triples :
                                print(s, p, o)

