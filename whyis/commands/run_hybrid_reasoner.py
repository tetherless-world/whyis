import flask
from flask import url_for, current_app
from flask_script import Command, Option
from flask import render_template
from flask import render_template_string
from nanopub import Nanopublication
import urllib.request, urllib.parse, urllib.error
import rdflib

from whyis.namespace import *


class RunHybridReasoner(Command):
    """Display all valid routes in the application"""
    def get_options(self):
        return [
            Option('--input', '-i', dest='reasoning_dict', required=True,
                   type=str),
            Option('--mode', '-m', dest='mode', help='Select reasoning mode', required=True,
                   type=str),
        ]

    def get_context(self,identifier,reasoning_dict,rule):
        context = {}
        #print(current_app.config[reasoning_dict][rule]["resource"] , identifier)
        context_vars = current_app.db.query('''SELECT DISTINCT * WHERE { %s 
        FILTER (regex(str(%s), "^(%s)"))
        }''' % (
        current_app.config[reasoning_dict][rule]["antecedent"] , current_app.config[reasoning_dict][rule]["resource"] , identifier), initNs=current_app.config[reasoning_dict][rule]["prefixes"])
        try :
            for key in context_vars.vars :
                try :
                    context[str(key)] = str(context_vars.bindings[0][key])
                except Exception as e:
                    print("Unable to set value for key ", key, " - ",str(e))
                    context[str(key)] = ""
        except Exception as e :
            print("Something went wrong trying to set the context dict:",e)
        try :
            for key in context :
                try :
                    context[key] = current_app.get_label(current_app.get_entity(rdflib.URIRef(context[key])))
                except Exception as e :
                    print("Error getting label for ", context[key],":",e)
        except Exception as e :
            print("Error getting label:",e)
        return context

    def run(self, reasoning_dict, mode):
        if mode == 'deductor' :
            if "active_profiles" and "reasoning_profiles" in current_app.config :
                for profile in current_app.config["active_profiles"] :
                    for rule_reference in current_app.config["reasoning_profiles"][profile] :
                        for rule in current_app.config[reasoning_dict] :
                            if current_app.config[reasoning_dict][rule]["reference"] == rule_reference :
                                print(rule_reference)
                                resource_identifier = current_app.db.query('''SELECT DISTINCT %s WHERE { %s }''' % ( current_app.config[reasoning_dict][rule]["resource"], current_app.config[reasoning_dict][rule]["antecedent"]), initNs=current_app.config[reasoning_dict][rule]["prefixes"] )
                                for i in resource_identifier :
                                    #print(i)
                                    npub = Nanopublication(store=current_app.db.store)
                                    #npub = Nanopublication()
                                    triples = current_app.db.query('''CONSTRUCT { %s } WHERE { %s FILTER NOT EXISTS { %s } 
                                    FILTER (regex(str(%s), "^(%s)"))
                                    }''' % ( current_app.config[reasoning_dict][rule]["consequent"], current_app.config[reasoning_dict][rule]["antecedent"], current_app.config[reasoning_dict][rule]["consequent"],current_app.config[reasoning_dict][rule]["resource"],i[0]), initNs=current_app.config[reasoning_dict][rule]["prefixes"] )
                                    try :
                                        for s, p, o in triples :
                                            print("Hybrid reasoner deductor adding: ", s, p, o)
                                            npub.assertion.add((s, p, o))
                                    except :
                                        for s, p, o, c in triples :
                                            print("Hybrid reasoner deductor adding: ", s, p, o)
                                            npub.assertion.add((s, p, o))
                                    try :
                                        npub.provenance.add((npub.assertion.identifier, prov.value, rdflib.Literal(flask.render_template_string(current_app.config[reasoning_dict][rule]["explanation"], **self.get_context(i[0],reasoning_dict,rule)))))
                                        #print(rule_reference,flask.render_template_string(current_app.config[reasoning_dict][rule]["explanation"], **self.get_context(i[0],reasoning_dict,rule)))
                                    except Exception as e :
                                        print("Unable to write explanation:", e)
        elif mode == 'abductor':
            if "active_profiles" and "reasoning_profiles" in current_app.config :
                for profile in current_app.config["active_profiles"] :
                    for rule_reference in current_app.config["reasoning_profiles"][profile] :
                        print(rule_reference)
                        for rule in current_app.config[reasoning_dict] :
                            if current_app.config[reasoning_dict][rule]["reference"] == rule_reference :
                                npub = Nanopublication(store=current_app.db.store)
                                #npub = Nanopublication()
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
        elif mode == 'plan_treatment' :
            #diabetes_therapies = current_app.db.query('''SELECT DISTINCT ?treatment WHERE {
#  GRAPH ?g { ?s a ?type . }
#  ?type rdfs:label ?treatment .
#  ?g prov:wasInformedBy ?observation .
#  FILTER(str(?observation)="http://purl.org/twc/dpo/kb/therapy: http://purl.org/twc/dpo/ont/FavorableDiabetesTherapy")
#}'''% ( ), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
            #treatment_dict = {}
            #for therapy in diabetes_therapies :
                #[str(therapy["treatment"])] = 0
            diabetes_therapy_categories = current_app.db.query('''SELECT DISTINCT ?treatment WHERE {
  ?type rdfs:label ?treatment ;
    rdfs:subClassOf dpo:AntihyperglycemicTreatment .
}'''% ( ), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
            treatment_category_dict = {}
            for category in diabetes_therapy_categories :
                treatment_category_dict[str(category["treatment"])] = 0

            diabetes_patients = current_app.db.query('''SELECT DISTINCT ?patient ?existingTherapy WHERE {
  ?patient rdf:type sio:Patient ;
    dpo:hasDiagnosis/rdf:type dpo:Diabetes .
  OPTIONAL{?patient dpo:hasTherapy ?existingTherapy .
    ?existingTherapy rdf:type/rdfs:subClassOf* dpo:AntihyperglycemicTreatment . }
}'''% ( ), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
            #patient_dict = {}
            patient_category_dict = {}
            patient_reasoning_dict = {}
            for patient in diabetes_patients :
                reasoning_justification = {}
                patient_reasoning_dict[str(patient["patient"])] = {}
                #patient_dict[str(patient["patient"])] = treatment_dict.copy()
                patient_category_dict[str(patient["patient"])] = treatment_category_dict.copy()
                preferences = current_app.db.query('''SELECT DISTINCT ?preference WHERE {
  <%s> dpo:hasTreatmentPreference/rdf:type ?preference .
}'''% (patient["patient"]), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
                for preference in preferences :
                    reasoning_justification[str(preference["preference"])]={}
                    preferred_therapies = current_app.db.query('''SELECT DISTINCT ?treatment ?category WHERE {
  GRAPH ?g { ?s a ?type . }
  ?type rdfs:label ?treatment .
  ?type rdfs:subClassOf/rdfs:label ?category .
  ?g prov:wasInformedBy ?observation .
  FILTER(str(?observation)="http://purl.org/twc/dpo/kb/therapy: %s")
}'''% ( preference["preference"] ), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
                    update_list = []
                    for preferred_therapy in preferred_therapies :
                        #patient_dict[str(patient["patient"])][str(preferred_therapy["treatment"])]+=1
                        if(str(preferred_therapy["treatment"]) in patient_category_dict[str(patient["patient"])].keys()) :
                            if (str(preferred_therapy["treatment"]) not in update_list) :
                                patient_category_dict[str(patient["patient"])][str(preferred_therapy["treatment"])]+=1
                                reasoning_justification[str(preference["preference"])][str(preferred_therapy["treatment"])]="+1"
                                update_list.append(str(preferred_therapy["treatment"]))
                        else:
                            if (str(preferred_therapy["category"]) in reasoning_justification[str(preference["preference"])].keys()) :
                                if(reasoning_justification[str(preference["preference"])][str(preferred_therapy["category"])]!="+1") :
                                    reasoning_justification[str(preference["preference"])][str(preferred_therapy["category"])]+="," + str(preferred_therapy["treatment"])
                            else :
                                reasoning_justification[str(preference["preference"])][str(preferred_therapy["category"])]=str(preferred_therapy["treatment"])
                            if (str(preferred_therapy["category"]) not in update_list ):
                                patient_category_dict[str(patient["patient"])][str(preferred_therapy["category"])]+=1
                                update_list.append(str(preferred_therapy["category"]))
                    update_list = []
                if(not patient["existingTherapy"]) :
                    patient_category_dict[str(patient["patient"])]["Biguanide"]+=1 # first line therapy adjustment
                    patient_reasoning_dict[str(patient["patient"])]["First Line Therapy"] = {"Biguanide":"Metformin"}
                patient_reasoning_dict[str(patient["patient"])]["Preferences"] = reasoning_justification
                reasoning_justification = {}
                aversions = current_app.db.query('''SELECT DISTINCT ?aversion WHERE {
  <%s> dpo:hasTreatmentAversion/rdf:type ?aversion .
}'''% (patient["patient"]), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
                for aversion in aversions :
                    reasoning_justification[str(aversion["aversion"])]={}
                    unpreferred_therapies = current_app.db.query('''SELECT DISTINCT ?treatment ?category WHERE {
  GRAPH ?g { ?s a ?type . }
  ?type rdfs:label ?treatment .
  ?type rdfs:subClassOf/rdfs:label ?category .
  ?g prov:wasInformedBy ?observation .
  FILTER(str(?observation)="http://purl.org/twc/dpo/kb/therapy: %s")
}'''% ( aversion["aversion"] ), initNs={ "owl" : "http://www.w3.org/2002/07/owl#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "sio" : "http://semanticscience.org/resource/", "prov" : "http://www.w3.org/ns/prov#" , "dpo" : "http://purl.org/twc/dpo/ont/", "dpo-kb" : "http://purl.org/twc/dpo/kb/"} )
                    update_list = []
                    for unpreferred_therapy in unpreferred_therapies :
                        #patient_dict[str(patient["patient"])][str(unpreferred_therapy["treatment"])]-=1
                        if(str(unpreferred_therapy["treatment"]) in patient_category_dict[str(patient["patient"])].keys()) : 
                            if(str(unpreferred_therapy["treatment"]) not in update_list):
                                patient_category_dict[str(patient["patient"])][str(unpreferred_therapy["treatment"])]-=1
                                reasoning_justification[str(aversion["aversion"])][str(unpreferred_therapy["treatment"])]="-1"
                                update_list.append(str(unpreferred_therapy["treatment"]))
                        #elif (str(unpreferred_therapy["category"]) not in update_list ):
                        #    patient_category_dict[str(patient["patient"])][str(unpreferred_therapy["category"])]-=1
                        #    reasoning_justification[str(aversion["aversion"])][str(unpreferred_therapy["category"])]="-1"
                        #    update_list.append(str(unpreferred_therapy["category"]))
                        else:
                            if (str(unpreferred_therapy["category"]) in reasoning_justification[str(aversion["aversion"])].keys()) :
                                if(reasoning_justification[str(aversion["aversion"])][str(unpreferred_therapy["category"])]!="-1") :
                                    reasoning_justification[str(aversion["aversion"])][str(unpreferred_therapy["category"])]+="," + str(unpreferred_therapy["treatment"])
                            else :
                                reasoning_justification[str(aversion["aversion"])][str(unpreferred_therapy["category"])]=str(unpreferred_therapy["treatment"])
                            if (str(unpreferred_therapy["category"]) not in update_list ):
                                patient_category_dict[str(patient["patient"])][str(unpreferred_therapy["category"])]-=1
                                update_list.append(str(unpreferred_therapy["category"]))
                    update_list = []
                patient_reasoning_dict[str(patient["patient"])]["Aversions"] = reasoning_justification
                reasoning_justification = {}
            
            for p in patient_category_dict.keys() :
                unsorted_dict = patient_category_dict[p]
                sorted_dict = sorted(unsorted_dict.items(), key=lambda x:x[1], reverse=True)
                #print(p,sorted_dict)
                patient_reasoning_dict[p]["Therapy Rankings"]=sorted_dict
            print(patient_reasoning_dict)
