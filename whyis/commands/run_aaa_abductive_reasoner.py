from flask import url_for, current_app
from flask_script import Command, Option
from nanopub import Nanopublication
import urllib.request, urllib.parse, urllib.error
import re
import os
import rdflib

class RunAAAReasoner(Command):
    """Display all valid routes in the application"""
    def get_options(self):
        return [
            Option('--input', '-i', dest='input_file', help='Specify the input ontology file', required=True, type=str),
            Option('--output', '-out', dest='output_file', help='Specify the file location where the results will be written to', required=True, type=str),
            Option('--depth', '-d', dest='depth', help='Specify the maximum length of explanations', required=True, type=str),
            Option('--abducibles', '-abd', dest='abducibles', help='Specify the abducibles used to limit the reasoning', required=True, type=str),
            Option('--observation', '-obs', dest='observation', help='Specify the observation that should be explained', required=True, type=str),
        ]

    def run(self, input_file, output_file, depth, abducibles, observation):
        npub = Nanopublication(store=current_app.db.store) 
        #java -Xmx4096m
        abductor_command = "java -jar jars/AAA.jar -abd \"" + abducibles + "\" -d " + depth + " -i " + input_file + " -l -obs \"" + observation + "\" -out " + output_file + " -r"
        print(abductor_command)
        os.system(abductor_command)
        
        input_details_start=""
        ontology_details_start=""
        time_details_start=""
        mhs_details_start=""
        explanations_start=""
        
        f = open(output_file,'r')
        lines = f.readlines()
        for n, line in enumerate(lines) :
            if("INPUT DETAILS" in line) : 
                input_details_start = n+1
            if("ONTOLOGY DETAILS" in line) : 
                ontology_details_start = n+1
            if("TIME DETAILS" in line) : 
                time_details_start = n+1
            if("MHS DETAILS" in line) : 
                mhs_details_start = n+1
            if("EXPLANATIONS" in line) : 
                explanations_start = n+1
                
        metadata=lines[0:input_details_start-1]
        input_details=lines[input_details_start:ontology_details_start-1]
        ontology_details=lines[ontology_details_start:time_details_start-1]
        time_details=lines[time_details_start:mhs_details_start-1]
        mhs_details=lines[mhs_details_start:explanations_start-1]
        explanations=lines[explanations_start:]

        #print(metadata)
        #print(input_details)
        #print(ontology_details)
        #print(time_details)
        #print(mhs_details)
        #print(explanations)

        if("no explanations" in explanations[0]) :
            print("Handle the case where there is no explanations!")
        else :
            explanations = explanations[1:]
            for explanation in explanations :
                explanation=explanation.replace(' ','') #remove any spaces
                explanation=explanation.lstrip('{') # get rid of first bracket
                explanation=explanation.rstrip('\n') #get rid of ending newline
                explanation=explanation.rstrip(',') #get rid of ending comma
                explanation=explanation.rstrip('}') #get rid of ending brackets 
                r = re.compile(r'(?:[^,(]|\([^)]*\))+') 
                explanation_set=r.findall(explanation) #create set from each explanation
                for exp in explanation_set :
                #    if 'not' in exp :
                #        print()
                #    if 'and' in exp :
                #        print()
                #    if 'or' in exp :
                #        print()
                #    if 'some' in exp :
                #        print()
                #    if 'all' in exp :
                #        print()
                    exp = exp.replace("http:","http;") #temporarily replace colons in http:
                    exp_terms = exp.split(":")
                    exp_terms[:] = [x if "http;" not in x else x.replace("http;","http:") for x in exp_terms] #replace the colons back in to http:
                    try :
                        npub.assertion.add((rdflib.URIRef(exp_terms[0]), rdflib.RDF.type, rdflib.URIRef(exp_terms[1])))
                    except Exception as e :
                        print("Unable to add assertion",exp_terms[0],":",exp_terms[1])
                        print("Error:",e)
