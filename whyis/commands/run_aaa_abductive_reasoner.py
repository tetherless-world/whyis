from flask import url_for, current_app
from flask_script import Command, Option
from nanopub import Nanopublication
import urllib.request, urllib.parse, urllib.error
import re
import os
import rdflib
import tempfile
from whyis.namespace import *

class RunAAAReasoner(Command):
    """Display all valid routes in the application"""
    def get_options(self):
        return [
            Option('--input', '-i', dest='input_file', help='Specify the input ontology file', required=True, type=str),
            Option('--output', '-out', dest='output_file', help='Specify the file location where the results will be written to', required=False, type=str),
            Option('--depth', '-d', dest='depth', help='Specify the maximum length of explanations', required=False, type=str),
            Option('--abducibles', '-abd', dest='abducibles', help='Specify the abducibles used to limit the reasoning', required=False, type=str),
            Option('--observation', '-obs', dest='observation', help='Specify the observation that should be explained. The observation must be in the form <individual>: <concept> or <ind1,ind2>: role; space after delimiter \':\' is required! Multiple observations are delimited by \';\'.', required=True, type=str),
            Option('--reduction', '-r', dest='reduction', help='To compute through reduction, specify Y or y', required=False, type=str),
            Option('--loops', '-l', dest='loops', help='To allow loops in relations amongst explanations, specify Y or y', required=False, type=str),
            Option('--negations', '-n', dest='negations', help='To compute WITHOUT negations, specify N or n. Otherwise, negations are included.', required=False, type=str),
            Option('--timeout', '-t', dest='timeout', help='To interrupt after a certain timeout, specify the number of seconds', required=False, type=str),
        ]

    def run(self, input_file, output_file, depth, abducibles, observation, reduction, loops, timeout, negations):
        input_details_start=""
        ontology_details_start=""
        time_details_start=""
        mhs_details_start=""
        explanations_start=""
        lines = []

        #java -Xmx4096m        
        abductor_command = "java -jar jars/AAA.jar" 
        if abducibles :
            abductor_command += " -abd \"" + abducibles + "\""
        if depth :
            abductor_command += " -d " + depth
        if timeout :
            abductor_command += " -t " + timeout
        if reduction and reduction.lower() == 'y':
            abductor_command +=  " -r"
        if loops and loops.lower() == 'y':
            abductor_command += " -l" 
        if negations and negations.lower() == 'n':
            abductor_command += " -n" 
        abductor_command += " -i " + input_file + " -obs \"" + observation + "\"" 
        
        if output_file :
            abductor_command += " -out " + output_file
            print(abductor_command)
            os.system(abductor_command)
            f = open(output_file,'r')
            lines = f.readlines()
            f.close()
        else :
            f = tempfile.NamedTemporaryFile('w+t')
            abductor_command += " -out " + f.name            
            print(abductor_command)
            os.system(abductor_command)
            f.seek(0)
            with open(f.name) as tmpfile :
                for tmpline in tmpfile :
                    lines.append(tmpline)
            f.close()

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
<<<<<<< HEAD
        #currentGraph = rdflib.ConjunctiveGraph() 
        #for (s,p,o) in current_app.db :
        #    currentGraph.add((s,p,o))

        npub_list = []
=======
        currentGraph = rdflib.ConjunctiveGraph() 
        for (s,p,o) in current_app.db :
            currentGraph.add((s,p,o))

>>>>>>> 51f7f568dce04127b20a733ef5b5935360e2adb5

        if("no explanations" in explanations[0]) :
            print("Handle the case where there is no explanations!")
        else :
            explanations = explanations[1:]
            for explanation in explanations :
                existing_exp_count = 0
<<<<<<< HEAD
                #npub = Nanopublication(store=current_app.db.store) # new nanopub per explanation
                npub = Nanopublication()
=======
                npub = Nanopublication(store=current_app.db.store) # new nanopub per explanation

>>>>>>> 51f7f568dce04127b20a733ef5b5935360e2adb5
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
                    if 'some' in exp :
                        predicate_start_location = exp.find('some') + 5
                        predicate_end_location = exp.find(',')
                        predicate_uri=exp[predicate_start_location:predicate_end_location]
                        object_start_location = exp.find('value') + 6
                        object_end_location = exp.find('))')
                        object_uri=exp[object_start_location:object_end_location]
                        exp = exp.replace("http:","http;") #temporarily replace colons in http:
                        exp_terms = exp.split(":")
                        exp_terms[:] = [x if "http;" not in x else x.replace("http;","http:") for x in exp_terms] #replace the colons back in to http:
<<<<<<< HEAD
                        if (rdflib.URIRef(exp_terms[0]), rdflib.URIRef(predicate_uri), rdflib.URIRef(object_uri)) in current_app.db :
=======
                        if (rdflib.URIRef(exp_terms[0]), rdflib.URIRef(predicate_uri), rdflib.URIRef(object_uri)) in currentGraph :
>>>>>>> 51f7f568dce04127b20a733ef5b5935360e2adb5
                            existing_exp_count += 1
                            print("Found existing assertion:",exp_terms[0],":",exp_terms[1])
                        try :
                            npub.assertion.add((rdflib.URIRef(exp_terms[0]), rdflib.URIRef(predicate_uri), rdflib.URIRef(object_uri)))
                        except Exception as e :
                            print("Unable to add assertion",exp_terms[0],":",exp_terms[1])
                            print("Error:",e)

                #    if 'all' in exp :
                #        print()
                    else :
                        exp = exp.replace("http:","http;") #temporarily replace colons in http:
                        exp_terms = exp.split(":")
                        exp_terms[:] = [x if "http;" not in x else x.replace("http;","http:") for x in exp_terms] #replace the colons back in to http:
<<<<<<< HEAD
                        if (rdflib.URIRef(exp_terms[0]), rdflib.RDF.type, rdflib.URIRef(exp_terms[1])) in current_app.db :
=======
                        if (rdflib.URIRef(exp_terms[0]), rdflib.RDF.type, rdflib.URIRef(exp_terms[1])) in currentGraph :
>>>>>>> 51f7f568dce04127b20a733ef5b5935360e2adb5
                            existing_exp_count += 1
                            print("Found existing assertion:",exp_terms[0],":",exp_terms[1])
                        try :
                            npub.assertion.add((rdflib.URIRef(exp_terms[0]), rdflib.RDF.type, rdflib.URIRef(exp_terms[1])))
                        except Exception as e :
                            print("Unable to add assertion",exp_terms[0],":",exp_terms[1])
                            print("Error:",e)
                if len(metadata) > 0 :
                    metadata_ref = rdflib.BNode()
                    npub.provenance.add((npub.assertion.identifier,prov.used,metadata_ref))
                    npub.provenance.add((metadata_ref,rdflib.RDF.type, sio.Metadata))
                    for metadata_detail in metadata :
                        npub.provenance.add((metadata_ref,skos.note,rdflib.Literal(metadata_detail)))
                if len(input_details) > 0 :
                    input_ref = rdflib.BNode()
                    npub.provenance.add((npub.assertion.identifier,prov.used,input_ref))
                    npub.provenance.add((input_ref,rdflib.RDF.type, sio.Parameter))
                    for input_detail in input_details :
                        npub.provenance.add((input_ref,skos.note,rdflib.Literal(input_detail)))
                if len(ontology_details) > 0 :
                    ontology_ref = rdflib.BNode()
                    npub.provenance.add((npub.assertion.identifier,prov.wasDerivedFrom,ontology_ref))
                    npub.provenance.add((ontology_ref,rdflib.RDF.type, owl.Ontology))
                    for ont_detail in ontology_details :
                        npub.provenance.add((ontology_ref,skos.note,rdflib.Literal(ont_detail)))
                if len(time_details) > 0 :
                    time_ref = rdflib.BNode()
                    npub.provenance.add((npub.assertion.identifier,prov.used,time_ref))
                    npub.provenance.add((time_ref,rdflib.RDF.type, sio.TimeMeasurement ))
                    for time_detail in time_details :
                        npub.provenance.add((time_ref,skos.note,rdflib.Literal(time_detail)))
                if len(mhs_details) > 0 :
                    mhs_ref = rdflib.BNode()
                    npub.provenance.add((npub.assertion.identifier,prov.used,mhs_ref))
                    npub.provenance.add((mhs_ref,rdflib.RDF.type, sio.Algorithm))
                    for mhs_detail in mhs_details :
                        npub.provenance.add((mhs_ref,skos.note,rdflib.Literal(mhs_detail)))
                npub.provenance.add((npub.assertion.identifier,rdflib.RDF.type,sio.Unsupported))
                print("Number of existing explanations for", npub.assertion.identifier, ":", existing_exp_count)
<<<<<<< HEAD
                npub_list.append(npub)
        for nanopub in npub_list :
            try:
                current_app.nanopub_manager.publish(nanopub)
            except Exception as e :
                print("Unable to publish nanopub:", nanopub)
                print("Error:",e)
=======
>>>>>>> 51f7f568dce04127b20a733ef5b5935360e2adb5
