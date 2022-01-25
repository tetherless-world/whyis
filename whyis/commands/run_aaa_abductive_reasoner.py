from flask import url_for, current_app
from flask_script import Command, Option
from nanopub import Nanopublication
import urllib.request, urllib.parse, urllib.error
import os

class RunAAAReasoner(Command):
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
        abducibles = "\"http://purl.org/twc/HEALS/ont/ClinicallyRelevantWeightGainPatient, http://purl.org/twc/HEALS/kb/jane, http://purl.org/twc/HEALS/ont/WeightGainPatient, http://purl.org/twc/HEALS/ont/ClinicallyRelevantWeightGain, http://purl.org/twc/HEALS/ont/Patient, http://semanticscience.org/resource/hasAttribute, http://purl.org/twc/HEALS/kb/clinicalWeightGain, http://purl.org/twc/HEALS/kb/clinicalBMIGain, http://purl.org/twc/HEALS/kb/biologicalEffect,	http://purl.org/twc/HEALS/kb/metabolismDecrease, http://purl.org/twc/HEALS/kb/hypothyroidism\""
        depth = "3"
        input_file = "examples/abductive_example.ttl" 
        observation = "\"http://purl.org/twc/HEALS/kb/jane: http://purl.org/twc/HEALS/ont/ClinicallyRelevantWeightGainPatient\"" 
        output_file = "output.txt" #java -Xmx4096m
        abductor_command = "java -jar jars/AAA.jar -abd " + abducibles + " -d " + depth + " -i " + input_file + " -l -obs " + observation + " -out " + output_file + "-r"
        print(abductor_command)
        os.system(abductor_command)
