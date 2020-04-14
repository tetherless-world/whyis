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

    def test_functional_object_property(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Functional Object Property -------

sio:Role rdf:type owl:Class ;
    rdfs:label "role" ;
    rdfs:subClassOf sio:RealizableEntity ;
    dct:description "A role is a realizable entity that describes behaviours, rights and obligations of an entity in some particular circumstance." .

sio:isAttributeOf rdf:type owl:ObjectProperty ;
    rdfs:label "is attribute of" ;
    dct:description "is attribute of is a relation that associates an attribute with an entity where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
    rdfs:subPropertyOf sio:isRelatedTo .

sio:hasAttribute rdf:type owl:ObjectProperty ;
    rdfs:label "has attribute" ;
    dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
    rdfs:subPropertyOf sio:isRelatedTo .

sio:isPropertyOf rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "is property of" ;
    dct:description "is property of is a relation betweena  quality, capability or role and the entity that it and it alone bears." ;
    rdfs:subPropertyOf sio:isAttributeOf .

sio:hasProperty rdf:type owl:ObjectProperty ,
                                owl:InverseFunctionalProperty;
    rdfs:label "has property" ;
    owl:inverseOf sio:isPropertyOf ;
    dct:description "has property is a relation between an entity and the quality, capability or role that it and it alone bears." ;
    rdfs:subPropertyOf sio:hasAttribute .

sio:hasRealizableProperty rdf:type owl:ObjectProperty ,
                                owl:InverseFunctionalProperty;
    rdfs:label "has realizable property" ;
    rdfs:subPropertyOf sio:hasProperty .

sio:isRealizablePropertyOf rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "is realizable property of" ;
    rdfs:subPropertyOf sio:isPropertyOf ;
    owl:inverseOf sio:hasRealizableProperty .

sio:isRoleOf rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "is role of" ;
    rdfs:domain sio:Role ;
    rdfs:subPropertyOf sio:isRealizablePropertyOf ;
    dct:description "is role of is a relation between a role and the entity that it is a property of." ;
    owl:inverseOf sio:hasRole .

sio:hasRole rdf:type owl:ObjectProperty ,
                                owl:InverseFunctionalProperty;
    rdfs:label "has role" ;
    rdfs:subPropertyOf sio:hasRealizableProperty ;
    dct:description "has role is a relation between an entity and a role that it bears." .

sio:Human  rdf:type owl:Class ;
    rdfs:label "human" ;
    rdfs:subClassOf sio:MulticellularOrganism ;
    dct:description "A human is a primates of the family Hominidae and are characterized by having a large brain relative to body size, with a well developed neocortex, prefrontal cortex and temporal lobes, making them capable of abstract reasoning, language, introspection, problem solving and culture through social learning." .

sio:MulticellularOrganism  rdf:type owl:Class ;
    rdfs:label "multicellular organism" ;
    rdfs:subClassOf sio:CellularOrganism ;
    dct:description "A multi-cellular organism is an organism that consists of more than one cell." .

sio:CellularOrganism  rdf:type owl:Class ;
    rdfs:label "cellular organism" ;
    rdfs:subClassOf sio:Organism ;
#    <owl:disjointWith rdf:resource="http://semanticscience.org/resource/Non-cellularOrganism"/>
    dct:description "A cellular organism is an organism that contains one or more cells." .

sio:Organism  rdf:type owl:Class ;
    rdfs:label "organism" ;
    rdfs:subClassOf sio:BiologicalEntity ;
    dct:description "A biological organisn is a biological entity that consists of one or more cells and is capable of genomic replication (independently or not)." .

sio:BiologicalEntity  rdf:type owl:Class ;
    rdfs:label "biological entity" ;
    rdfs:subClassOf sio:HeterogeneousSubstance ;
    dct:description "A biological entity is a heterogeneous substance that contains genomic material or is the product of a biological process." .

sio:HeterogeneousSubstance  rdf:type owl:Class ;
    rdfs:label "heterogeneous substance" ;
    rdfs:subClassOf sio:MaterialEntity ;
    rdfs:subClassOf sio:ChemicalEntity ;
#    <owl:disjointWith rdf:resource="http://semanticscience.org/resource/HomogeneousSubstance"/>
    dct:description "A heterogeneous substance is a chemical substance that is composed of more than one different kind of component." .

sio:MaterialEntity  rdf:type owl:Class ;
    rdfs:label "material entity" ;
    rdfs:subClassOf sio:Object ;
#    <rdfs:subClassOf rdf:nodeID="arc0158b11"/>
#    <rdfs:subClassOf rdf:nodeID="arc0158b12"/>
    dct:description "A material entity is a physical entity that is spatially extended, exists as a whole at any point in time and has mass." .

sio:ChemicalEntity  rdf:type owl:Class ;
    rdfs:label "chemical entity" ;
    rdfs:subClassOf sio:MaterialEntity ;
#    <sio:equivalentTo>CHEBI:23367</sio:equivalentTo>
    dct:description "A chemical entity is a material entity that pertains to chemistry." .

ex-kb:Mother rdf:type owl:Individual ;
    rdfs:label "mother" ;
    sio:isRoleOf ex-kb:Sarah ;
    sio:inRelationTo ex-kb:Tim .

ex-kb:Sarah rdf:type sio:Human ;
    rdfs:label "Sarah" .

ex-kb:Tim rdf:type sio:Human ;
    rdfs:label "Tim" .

# Expect that "ex-kb:Sarah sio:hasRole ex-kb:Mother ." is returned
# ------- Functional Object Property ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Functional Object Property"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Sarah'))[SIO.hasRole:URIRef('http://example.com/kb/example#Mother')])

    def test_domain_restriction(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Domain Restriction -------   
sio:Role rdf:type owl:Class ;
    rdfs:label "role" ;
    rdfs:subClassOf sio:RealizableEntity ;
    dct:description "A role is a realizable entity that describes behaviours, rights and obligations of an entity in some particular circumstance." .

sio:isAttributeOf rdf:type owl:ObjectProperty ;
    rdfs:label "is attribute of" ;
    dct:description "is attribute of is a relation that associates an attribute with an entity where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
    rdfs:subPropertyOf sio:isRelatedTo .

sio:hasAttribute rdf:type owl:ObjectProperty ;
    rdfs:label "has attribute" ;
    dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
    rdfs:subPropertyOf sio:isRelatedTo .

sio:isPropertyOf rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "is property of" ;
    dct:description "is property of is a relation betweena  quality, capability or role and the entity that it and it alone bears." ;
    rdfs:subPropertyOf sio:isAttributeOf .

sio:hasProperty rdf:type owl:ObjectProperty ,
                                owl:InverseFunctionalProperty;
    rdfs:label "has property" ;
    owl:inverseOf sio:isPropertyOf ;
    dct:description "has property is a relation between an entity and the quality, capability or role that it and it alone bears." ;
    rdfs:subPropertyOf sio:hasAttribute .

sio:hasRealizableProperty rdf:type owl:ObjectProperty ,
                                owl:InverseFunctionalProperty;
    rdfs:label "has realizable property" ;
    rdfs:subPropertyOf sio:hasProperty .

sio:isRealizablePropertyOf rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "is realizable property of" ;
    rdfs:subPropertyOf sio:isPropertyOf ;
    owl:inverseOf sio:hasRealizableProperty .

sio:isRoleOf rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "is role of" ;
    rdfs:domain sio:Role ;
    rdfs:subPropertyOf sio:isRealizablePropertyOf ;
    dct:description "is role of is a relation between a role and the entity that it is a property of." ;
    owl:inverseOf sio:hasRole .

sio:hasRole rdf:type owl:ObjectProperty ,
                                owl:InverseFunctionalProperty;
    rdfs:label "has role" ;
    rdfs:subPropertyOf sio:hasRealizableProperty ;
    dct:description "has role is a relation between an entity and a role that it bears." .

sio:Human  rdf:type owl:Class ;
    rdfs:label "human" ;
    rdfs:subClassOf sio:MulticellularOrganism ;
    dct:description "A human is a primates of the family Hominidae and are characterized by having a large brain relative to body size, with a well developed neocortex, prefrontal cortex and temporal lobes, making them capable of abstract reasoning, language, introspection, problem solving and culture through social learning." .

sio:MulticellularOrganism  rdf:type owl:Class ;
    rdfs:label "multicellular organism" ;
    rdfs:subClassOf sio:CellularOrganism ;
    dct:description "A multi-cellular organism is an organism that consists of more than one cell." .

sio:CellularOrganism  rdf:type owl:Class ;
    rdfs:label "cellular organism" ;
    rdfs:subClassOf sio:Organism ;
#    <owl:disjointWith rdf:resource="http://semanticscience.org/resource/Non-cellularOrganism"/>
    dct:description "A cellular organism is an organism that contains one or more cells." .

sio:Organism  rdf:type owl:Class ;
    rdfs:label "organism" ;
    rdfs:subClassOf sio:BiologicalEntity ;
    dct:description "A biological organisn is a biological entity that consists of one or more cells and is capable of genomic replication (independently or not)." .

sio:BiologicalEntity  rdf:type owl:Class ;
    rdfs:label "biological entity" ;
    rdfs:subClassOf sio:HeterogeneousSubstance ;
    dct:description "A biological entity is a heterogeneous substance that contains genomic material or is the product of a biological process." .

sio:HeterogeneousSubstance  rdf:type owl:Class ;
    rdfs:label "heterogeneous substance" ;
    rdfs:subClassOf sio:MaterialEntity ;
    rdfs:subClassOf sio:ChemicalEntity ;
#    <owl:disjointWith rdf:resource="http://semanticscience.org/resource/HomogeneousSubstance"/>
    dct:description "A heterogeneous substance is a chemical substance that is composed of more than one different kind of component." .

sio:MaterialEntity  rdf:type owl:Class ;
    rdfs:label "material entity" ;
    rdfs:subClassOf sio:Object ;
#    <rdfs:subClassOf rdf:nodeID="arc0158b11"/>
#    <rdfs:subClassOf rdf:nodeID="arc0158b12"/>
    dct:description "A material entity is a physical entity that is spatially extended, exists as a whole at any point in time and has mass." .

sio:ChemicalEntity  rdf:type owl:Class ;
    rdfs:label "chemical entity" ;
    rdfs:subClassOf sio:MaterialEntity ;
#    <sio:equivalentTo>CHEBI:23367</sio:equivalentTo>
    dct:description "A chemical entity is a material entity that pertains to chemistry." .

ex-kb:Mother rdf:type owl:Individual ;
    rdfs:label "mother" ;
    sio:isRoleOf ex-kb:Sarah ;
    sio:inRelationTo ex-kb:Tim .

ex-kb:Sarah rdf:type sio:Human ;
    rdfs:label "Sarah" .

ex-kb:Tim rdf:type sio:Human ;
    rdfs:label "Tim" .

# Expect that "ex-kb:Mother rdf:type sio:Role ." is returned
# ------- Domain Restriction ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Domain Restriction"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Mother'))[RDF.type:URIRef('http://semanticscience.org/resource/Role')])

    def test_range_restriction(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------Range Restriction -------
sio:UnitOfMeasurement rdf:type owl:Class ;
    rdfs:label "unit of measurement" ;
    rdfs:subClassOf sio:Quantity ;
    dct:description "A unit of measurement is a definite magnitude of a physical quantity, defined and adopted by convention and/or by law, that is used as a standard for measurement of the same physical quantity." .

sio:hasUnit rdf:type owl:ObjectProperty ,
                                owl:FunctionalProperty;
    rdfs:label "has unit" ;
    owl:inverseOf sio:isUnitOf ;
    rdfs:range sio:UnitOfMeasurement ;
    rdfs:subPropertyOf sio:hasAttribute ;
    dct:description "has unit is a relation between a quantity and the unit it is a multiple of." .

sio:isUnitOf rdf:type owl:ObjectProperty ;
    rdfs:label "is unit of" ;
    rdfs:domain sio:UnitOfMeasurement ;
    rdfs:subPropertyOf sio:isAttributeOf ;
    dct:description "is unit of is a relation between a unit and a quantity that it is a multiple of." .

sio:Height rdf:type owl:Class ;
    rdfs:label "height" ;
    rdfs:subClassOf sio:1DExtentQuantity ;
    dct:description "Height is the one dimensional extent along the vertical projection of a 3D object from a base plane of reference." .

sio:1DExtentQuantity rdf:type owl:Class ;
    rdfs:label "1D extent quantity" ;
    rdfs:subClassOf sio:SpatialQuantity ;
    dct:description "A quantity that extends in single dimension." .

sio:SpatialQuantity rdf:type owl:Class ;
    rdfs:label "spatial quantity" ;
    rdfs:subClassOf sio:DimensionalQuantity ;
#    <rdfs:subClassOf rdf:nodeID="arc0158b33"/>
#    <rdfs:subClassOf rdf:nodeID="arc0158b34"/>
#    <sio:hasSynonym xml:lang="en">physical dimensional quantity</sio:hasSynonym>
    dct:description "A spatial quantity is a quantity obtained from measuring the spatial extent of an entity." .

sio:DimensionalQuantity rdf:type owl:Class ;
    rdfs:label "dimensional quantity" ;
    rdfs:subClassOf sio:Quantity ,
        [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasUnit ;
            owl:someValuesFrom sio:UnitOfMeasurement ] ;
    dct:description "A dimensional quantity is a quantity that has an associated unit." .

ex-kb:Tom rdf:type sio:Human ;
    rdfs:label "Tom" ;
    sio:hasAttribute ex-kb:HeightOfTom .

ex-kb:HeightOfTom rdf:type sio:Height ;
    sio:hasUnit ex-kb:Meter .

ex-kb:Meter rdf:type owl:Individual ;
    rdfs:label "meter" .

# Expect that "ex-kb:Meter rdf:type sio:UnitOfMeasurement" is returned
# ------- Range Restriction ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Range Restriction"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Meter'))[RDF.type:URIRef('http://semanticscience.org/resource/UnitOfMeasurement')])


#    def test_inverse_functional_object_property(self):
#        self.dry_run = False
#
#        np = nanopub.Nanopublication()
#        np.assertion.parse(data=prefixes+'''
# <------- Inverse Functional Object Property ------- 
# ------- Inverse Functional Object Property ------->
#''', format="turtle")
#        agent =  config.Config["inference_rules"]["Inverse Functional Object Property"]
#
#        results = self.run_agent(agent, nanopublication=np)
#        self.assertTrue(results[0].resource(URIRef(''))[RDF.type:URIRef('')])

    def test_functional_data_property(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Functional Data Property -------

sio:hasValue rdf:type owl:DatatypeProperty ,
                                owl:FunctionalProperty;
    rdfs:label "has value" ;
    dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

ex-kb:HeightOfTom sio:hasValue "5"^^xsd:integer .
ex-kb:HeightOfTom sio:hasValue "6"^^xsd:integer .
# ------- Functional Data Property ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Functional Data Property"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#HeightOfTom'))[RDF.type:OWL.Nothing])

    def test_property_disjointness(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Property Disjointness -------
ex:hasMother rdf:type owl:ObjectProperty ;
    rdfs:subPropertyOf sio:hasAttribute ;
    rdfs:label "has mother" ;
    owl:propertyDisjointWith ex:hasFather .

ex:hasFather rdf:type owl:ObjectProperty ;
    rdfs:label "has father" .

ex-kb:Jordan rdf:type sio:Human ;
    rdfs:label "Jordan" .

ex-kb:Susan rdf:type sio:Human ;
    rdfs:label "Susan" ;
    ex:hasFather ex-kb:Jordan ;
    ex:hasMother ex-kb:Jordan .

# ------- Property Disjointness ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Property Disjointness"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Susan'))[RDF.type:OWL.Nothing])

    def test_object_property_symmetry(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Symmetry -------
sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                owl:SymmetricProperty ;
    rdfs:label "is related to" ;
    dct:description "A is related to B iff there is some relation between A and B." .

ex-kb:Peter rdf:type sio:Human ;
    rdfs:label "Peter" ;
    sio:isRelatedTo ex-kb:Samantha .

ex-kb:Samantha rdf:type sio:Human ;
    rdfs:label "Samantha" .

# ------- Object Property Symmetry ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Object Property Symmetry"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Samantha'))[SIO.isRelatedTo:URIRef('http://example.com/kb/example#Peter')])

    def test_object_property_asymmetry(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Asymmetry -------
sio:isProperPartOf rdf:type owl:ObjectProperty ,
                                owl:AsymmetricProperty ,
                                owl:IrreflexiveProperty ;
    rdfs:label "is proper part of" ;
    rdfs:subPropertyOf sio:isPartOf ;
    dct:description "is proper part of is an asymmetric, irreflexive (normally transitive) relation between a part and its distinct whole." .

ex-kb:Nose rdf:type owl:Individual ;
    rdfs:label "nose" ;
    sio:isProperPartOf ex-kb:Face .

ex-kb:Face rdf:type owl:Individual ;
    sio:isProperPartOf ex-kb:Nose ;
    rdfs:label "face" .

# ------- Object Property Asymmetry ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Object Property Asymmetry"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Face'))[RDF.type:OWL.Nothing])

#    def test_class_inclusion(self):
#        self.dry_run = False
#
#        np = nanopub.Nanopublication()
#        np.assertion.parse(data=prefixes+'''
# <------- Class Inclusion ------- 
# ------- Class Inclusion ------->
#''', format="turtle")
#        agent =  config.Config["inference_rules"]["Class Inclusion"]
#
#        results = self.run_agent(agent, nanopublication=np)
#        self.assertTrue(results[0].resource(URIRef(''))[RDF.type:URIRef('')])

    def test_object_property_inclusion(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Inclusion -------
sio:Age rdf:type owl:Class ;
    rdfs:label "age" ;
    rdfs:subClassOf sio:DimensionalQuantity ;
    dct:description "Age is the length of time that a person has lived or a thing has existed." .

sio:DimensionlessQuantity rdf:type owl:Class ;
    rdfs:label "dimensionless quantity" ;
    rdfs:subClassOf sio:Quantity ,
        [ rdf:type owl:Class ;
            owl:complementOf [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasUnit ;
                owl:someValuesFrom sio:UnitOfMeasurement ] ];
    owl:disjointWith sio:DimensionalQuantity ;
    dct:description "A dimensionless quantity is a quantity that has no associated unit." .

sio:Quantity rdf:type owl:Class ;
    rdfs:label "quantity" ;
    owl:equivalentClass 
        [ rdf:type owl:Class ; 
            owl:unionOf (sio:DimensionlessQuantity sio:DimensionalQuantity) ] ;
    rdfs:subClassOf sio:MeasurementValue ;
#    <rdfs:subClassOf rdf:nodeID="arc0158b38"/>
#    <rdfs:subClassOf rdf:nodeID="arc0158b39"/>
    dct:description "A quantity is an informational entity that gives the magnitude of a property." .

sio:MeasurementValue rdf:type owl:Class ;
    rdfs:label "measurement value" ;
    rdfs:subClassOf sio:Number ;
#    <rdfs:subClassOf rdf:nodeID="arc0158b47"/>
    dct:description "A measurement value is a quantitative description that reflects the magnitude of some attribute." .

sio:Number rdf:type owl:Class ;
    rdfs:label "number" ;
    rdfs:subClassOf sio:MathematicalEntity ;
    dct:description "A number is a mathematical object used to count, label, and measure." .

ex-kb:Samantha sio:hasProperty ex-kb:AgeOfSamantha .

ex-kb:AgeOfSamantha rdf:type sio:Age ;
    rdfs:label "Samantha's age" .
# ------- Object Property Inclusion ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Object Property Inclusion "]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Samantha'))[sio.hasAttribute.type:URIRef('http://example.com/kb/example#AgeOfSamantha'))

    def test_data_property_inclusion(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Inclusion -------
ex:hasExactValue rdf:type owl:DatatypeProperty ;
    rdfs:label "has exact value" ;
    rdfs:subPropertyOf sio:hasValue .

ex-kb:AgeOfSamantha ex:hasExactValue "25.82"^^xsd:decimal .
# ------- Data Property Inclusion ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Data Property Inclusion"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#AgeOfSamantha'))[SIO.hasValue:Literal('25.82')])

    def test_class_equivalence (self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Equivalence -------
ex:Fake rdf:type owl:Class ;
    owl:equivalentClass sio:Fictional ;
    rdfs:label "fake" .

ex-kb:Hubert rdf:type ex:Fake ;
    rdfs:label "Hubert" .
# ------- Class Equivalence ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Class Equivalence"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#Hubert'))[RDF.type:URIRef('http://semanticscience.org/resource/Fictional')])

    def test_property_equivalence(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Property Equivalence -------
ex:hasValue rdf:type owl:DatatypeProperty ;
    rdfs:label "has value" ;
    owl:equivalentProperty sio:hasValue .
# ------- Property Equivalence ------->
''', format="turtle")
        agent =  config.Config["inference_rules"]["Property Equivalence"]

        results = self.run_agent(agent, nanopublication=np)
        self.assertTrue(results[0].resource(URIRef('http://example.com/kb/example#AgeOfSamantha'))[URIRef('http://example.com/ont/example#hasValue'):Literal('25.82')])

