import os
from base64 import b64encode

from rdflib import *

import json
from io import StringIO

from whyis import nanopub

from whyis import autonomic
from whyis.test.agent_unit_test_case import AgentUnitTestCase

prefixes = '''@prefix ncit: <http://purl.obolibrary.org/obo/NCIT_> .
@prefix uo: <http://purl.obolibrary.org/obo/UO_> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sio: <http://semanticscience.org/resource/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix ex: <http://example.com/ont/example#> .
@prefix ex-kb: <http://example.com/kb/example#> .
'''
class DeductorAgentTestCase(AgentUnitTestCase):
    def test_class_disjointness(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Disjointness -------

sio:Entity rdf:type owl:Class ;
    rdfs:label "entity" ;
    dct:description "Every thing is an entity." .

sio:Attribute rdf:type owl:Class ;
    rdfs:subClassOf sio:Entity ;
    rdfs:label "attribute" ;
    #<rdfs:subClassOf rdf:nodeID="arc0158b301"/>
    dct:description "An attribute is a characteristic of some entity." .

sio:RealizableEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:Attribute ;
    #<rdfs:subClassOf rdf:nodeID="arc0158b179"/>
    #<rdfs:subClassOf rdf:nodeID="arc0158b180"/>
    dct:description "A realizable entity is an attribute that is exhibited under some condition and is realized in some process." ;
    rdfs:label "realizable entity" .

sio:Quality rdf:type owl:Class ;
    rdfs:subClassOf sio:Attribute ;
    owl:disjointWith sio:RealizableEntity ;
    #<rdfs:subClassOf rdf:nodeID="arc0158b16"/>
    dct:description "A quality is an attribute that is intrinsically associated with its bearer (or its parts), but whose presence/absence and observed/measured value may vary." ;
    rdfs:label "quality" .

sio:ExistenceQuality rdf:type owl:Class ;
    rdfs:subClassOf sio:Quality ;
    dct:description "existence quality is the quality of an entity that describe in what environment it is known to exist." ;
    rdfs:label "existence quality" .

sio:Virtual rdf:type owl:Class ;
    rdfs:subClassOf sio:ExistenceQuality ;
    dct:description "virtual is the quality of an entity that exists only in a virtual setting such as a simulation or game environment." ;
    rdfs:label "virtual" .

sio:Real rdf:type owl:Class ;
    rdfs:subClassOf sio:ExistenceQuality ;
    owl:disjointWith sio:Fictional ;
    owl:disjointWith sio:Virtual ;
    dct:description "real is the quality of an entity that exists in real space and time." ;
    rdfs:label "real" .

sio:Hypothetical rdf:type owl:Class ;
    rdfs:subClassOf sio:ExistenceQuality ;
    dct:description "hypothetical is the quality of an entity that is conjectured to exist." ;
    rdfs:label "hypothetical" .

sio:Fictional rdf:type owl:Class ;
    rdfs:subClassOf sio:Hypothetical ;
    dct:description "fictional is the quality of an entity that exists only in a creative work of fiction." ;
    rdfs:label "fictional" .

ex-kb:ImaginaryFriend
    rdfs:label "my imaginary friend" ;
    rdf:type sio:Real ;
    rdf:type sio:Fictional .

# Should return ex-kb:ImaginaryFriend rdf:type owl:Nothing .

# ------- Class Disjointness ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Class Disjointness"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#ImaginaryFriend'))[RDF.type:OWL.Nothing])

    def test_object_property_transitivity(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Transitivity -------

sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                owl:SymmetricProperty ;
    rdfs:label "is related to" ;
    dct:description "A is related to B iff there is some relation between A and B." .

sio:isSpatiotemporallyRelatedTo rdf:type owl:ObjectProperty ,
                                owl:SymmetricProperty ;
    rdfs:subPropertyOf sio:isRelatedTo ;
    rdfs:label "is spatiotemporally related to" ;
    dct:description "A is spatiotemporally related to B iff A is in the spatial or temporal vicinity of B" .

sio:isLocationOf rdf:type owl:ObjectProperty ,
                                owl:TransitiveProperty ;
    rdfs:subPropertyOf sio:isSpatiotemporallyRelatedTo ;
    rdfs:label "is location of" ;
    dct:description "A is location of B iff the spatial region occupied by A has the spatial region occupied by B as a part." .

sio:hasPart rdf:type owl:ObjectProperty ,
                                owl:TransitiveProperty ,
                                owl:ReflexiveProperty ;
    rdfs:subPropertyOf sio:isLocationOf ;
    owl:inverseOf sio:isPartOf ;
    rdfs:label "has part" ;
    dct:description "has part is a transitive, reflexive and antisymmetric relation between a whole and itself or a whole and its part" .

sio:isLocatedIn rdf:type owl:ObjectProperty ,
                                owl:TransitiveProperty ;
    rdfs:subPropertyOf sio:isSpatiotemporallyRelatedTo ;
    rdfs:label "is located in" ;
    dct:description "A is located in B iff the spatial region occupied by A is part of the spatial region occupied by B." .

sio:isPartOf rdf:type owl:ObjectProperty ,
                                owl:TransitiveProperty ,
                                owl:ReflexiveProperty ;
    rdfs:subPropertyOf sio:isLocatedIn ;
    rdfs:label "is part of" ;
    dct:description "is part of is a transitive, reflexive and anti-symmetric mereological relation between a whole and itself or a part and its whole." .

ex-kb:Fingernail rdf:type owl:Individual ;
    rdfs:label "finger nail" ;
    sio:isPartOf ex-kb:Finger .

ex-kb:Finger rdf:type owl:Individual ;
    rdfs:label "finger" ;
    sio:isPartOf ex-kb:Hand . 

ex-kb:Hand rdf:type owl:Individual ;
    rdfs:label "hand" .

# should return "ex-kb:Fingernail sio:isPartOf ex-kb:Hand ."
# ------- Object Property Transitivity ------->

''', format="turtle")
        agent =  config.Config["inference_rules"]["Object Property Transitivity"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Fingernail'))[SIO.isPartOf:URIRef('http://example.com/kb/example#Hand')])

    def test_object_property_reflexivity(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Reflexivity  -------
sio:hasPart rdf:type owl:ObjectProperty ,
                                owl:TransitiveProperty ,
                                owl:ReflexiveProperty ;
    rdfs:subPropertyOf sio:isLocationOf ;
    owl:inverseOf sio:isPartOf ;
    rdfs:label "has part" ;
    dct:description "has part is a transitive, reflexive and antisymmetric relation between a whole and itself or a whole and its part" .

sio:Process rdf:type owl:Class ;
    rdfs:subClassOf sio:Entity ;
#    <rdfs:subClassOf rdf:nodeID="arc0158b17"/>
#    <rdfs:subClassOf rdf:nodeID="arc0158b18"/>
    dct:description "A process is an entity that is identifiable only through the unfolding of time, has temporal parts, and unless otherwise specified/predicted, cannot be identified from any instant of time in which it exists." ;
    rdfs:label "process" .

ex-kb:Workflow rdf:type sio:Process ;
    rdfs:label "workflow" ;
    sio:hasPart ex-kb:Step .

ex-kb:Step rdf:type sio:Process ;
    rdfs:label "step" .

# Should return "ex-kb:Workflow sio:hasPart ex-kb:Workflow ." is returned
# ------- Object Property Reflexivity  ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Object Property Reflexivity"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Workflow'))[SIO.hasPart:URIRef('http://example.com/kb/example#Workflow')])

    def test_object_property_irreflexivity(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Irreflexivity  -------
sio:hasMember rdf:type owl:ObjectProperty ,
                                owl:IrreflexiveProperty ;
    rdfs:subPropertyOf sio:hasAttribute ;
    owl:inverseOf sio:isMemberOf ;
    rdfs:label "has member" ;
    dct:description "has member is a mereological relation between a collection and an item." .

sio:isMemberOf rdf:type owl:ObjectProperty ;
    rdfs:subPropertyOf sio:isAttributeOf ;
    rdfs:label "is member of" ;
    dct:description "is member of is a mereological relation between a item and a collection." .

sio:Collection rdf:type owl:Class ;
    rdfs:subClassOf sio:Set ;
    rdfs:label "collection" ;
    dct:description "A collection is a set for which there exists at least one member, although any member need not to exist at any point in the collection's existence." .

sio:Set rdf:type owl:Class ;
    rdfs:subClassOf sio:MathematicalEntity ;
    rdfs:label "set" ;
    dct:description "A set is a collection of entities, for which there may be zero members." .

sio:MathematicalEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:InformationContentEntity ;
    rdfs:label "mathematical entity" ;
    dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .

sio:InformationContentEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:Object ;
#    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
    rdfs:label "information content entity" ;
    dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

ex-kb:Group rdf:type sio:Collection ;
    rdfs:label "group" ;
    sio:hasMember ex-kb:Group .

# Should return ex-kb:Group rdf:type owl:Nothing

# ------- Object Property Irreflexivity  ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Object Property Irreflexivity"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Group'))[RDF.type:OWL.Nothing])

