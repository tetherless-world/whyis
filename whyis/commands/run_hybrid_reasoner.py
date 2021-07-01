from flask import url_for, current_app
from flask_script import Command, Option
from nanopub import Nanopublication
import urllib.request, urllib.parse, urllib.error


class RunHybridReasoner(Command):
    """Display all valid routes in the application"""
    def get_options(self):
        return [
            Option('--input', '-i', dest='reasoning_dict', required=True,
                   type=str),
            Option('--mode', '-m', dest='mode', help='Select reasoning mode (either deductor or abductor)', required=True,
                   type=str),
        ]

    def run(self, reasoning_dict, mode):
        npub = Nanopublication(store=current_app.db.store)
        if mode == 'deductor' :
            if "active_profiles" and "reasoning_profiles" in current_app.config :
                for profile in current_app.config["active_profiles"] :
                    for rule_reference in current_app.config["reasoning_profiles"][profile] :
                        for rule in current_app.config[reasoning_dict] :
                            if current_app.config[reasoning_dict][rule]["reference"] == rule_reference :
                                print(rule_reference)
                                triples = current_app.db.query('''CONSTRUCT { %s } WHERE { %s FILTER NOT EXISTS { %s } } ''' % ( current_app.config[reasoning_dict][rule]["consequent"], current_app.config[reasoning_dict][rule]["antecedent"], current_app.config[reasoning_dict][rule]["consequent"]), initNs=current_app.config[reasoning_dict][rule]["prefixes"] )
                                for s, p, o, c in triples :
                                    print("Hybrid reasoner deductor adding: ", s, p, o)
                                    npub.assertion.add((s, p, o))
        elif mode == 'abductor':
            if "active_profiles" and "reasoning_profiles" in current_app.config :
                for profile in current_app.config["active_profiles"] :
                    for rule_reference in current_app.config["reasoning_profiles"][profile] :
                        print(rule_reference)
                        for rule in current_app.config[reasoning_dict] :
                            if current_app.config[reasoning_dict][rule]["reference"] == rule_reference :
                                triples = current_app.db.query('''
    CONSTRUCT {
        ?g2 <http://purl.org/ontology/sets/ont#hypothesis>
            [ a <http://purl.org/ontology/sets/ont#Hypothesis> , %s ; 
                rdfs:label "%s" ; 
                <http://purl.org/ontology/sets/ont#antecedentGraph> ?g1 
            ]  .
    } WHERE {
        GRAPH ?g1 { %s }
        GRAPH ?g2 { %s }
        FILTER NOT EXISTS {
            ?g2 <http://purl.org/ontology/sets/ont#hypothesis>
                [ a <http://purl.org/ontology/sets/ont#Hypothesis> , %s ; 
                    rdfs:label "%s" ; 
                    <http://purl.org/ontology/sets/ont#antecedentGraph> ?g1 
                ] .
        }
    }'''% ( current_app.config[reasoning_dict][rule]["rule"], current_app.config[reasoning_dict][rule]["reference"], current_app.config[reasoning_dict][rule]["antecedent"], current_app.config[reasoning_dict][rule]["consequent"], current_app.config[reasoning_dict][rule]["rule"], current_app.config[reasoning_dict][rule]["reference"]), initNs=current_app.config[reasoning_dict][rule]["prefixes"] )
                                for s, p, o, c in triples :
                                    print("Hybrid reasoner abductor adding: ", s, p, o)
                                    npub.assertion.add((s, p, o))

