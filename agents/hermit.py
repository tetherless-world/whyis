import nltk, re, pprint
from whyis import autonomic
from bs4 import BeautifulSoup
from rdflib import *
from slugify import slugify
from whyis import nanopub
from math import log10
import collections
import os
import javabridge

from whyis.namespace import sioc_types, sioc, sio, dc, prov, whyis

class ConsistencyCheck(autonomic.UpdateChangeService):
    activity_class = whyis.ConsistencyCheck

    def getInputClass(self):
        return sioc.Post

    def getOutputClass(self):
        return URIRef("http://purl.org/dc/dcmitype/Text")

    def get_query(self):
        return '''select ?resource where { ?resource <http://rdfs.org/sioc/ns#content> [].}'''

    def process(self, i, o):
        javabridge.start_vm(class_path=javabridge.JARS+["/apps/whyis/jars/whyis-java-jar-with-dependencies.jar"],run_headless=True)
        try:
            javabridge.run_script('edu.rpi.tw.whyis.HermiTAgent.reason();',
                dict(greetee='world'))
        finally:
            javabridge.kill_vm()
