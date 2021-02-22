import os
from base64 import b64encode

from rdflib import *

import json
from io import StringIO

from whyis import nanopub

from whyis.config_utils import import_config_module
config = import_config_module()

from whyis import autonomic
from whyis.test.agent_unit_test_case import AgentUnitTestCase

SIO = Namespace("http://semanticscience.org/resource/")
ONT = Namespace("http://example.com/ont/example#")
KB = Namespace("http://example.com/kb/example#")
WHYIS = Namespace("http://vocab.rpi.edu/whyis/")

prefixes = '''@prefix uo: <http://purl.obolibrary.org/obo/UO_> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sio: <http://semanticscience.org/resource/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix whyis: <http://vocab.rpi.edu/whyis/> .
@prefix ex: <http://example.com/ont/example#> .
@prefix ex-kb: <http://example.com/kb/example#> .
'''
class BackTracerAgentTestCase(AgentUnitTestCase):
    def test_class_disjointness_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Disjointness -------
ex-kb:Assertion_1 {
    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

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
}

ex-kb:Assertion_2 {
    ex-kb:ImaginaryFriend rdf:type owl:Nothing .
}
# ------- Class Disjointness ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Class Disjointness Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Class Disjointness Back Tracer')), self.app.db)

    def test_object_property_transitivity_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Transitivity -------
ex-kb:Assertion_1 {
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
}

ex-kb:Assertion_2 {
    ex-kb:Fingernail sio:isPartOf ex-kb:Hand .
}
# ------- Object Property Transitivity ------->

''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Transitivity Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Transitivity Back Tracer')), self.app.db)

    def test_object_property_reflexivity_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Reflexivity  -------
ex-kb:Assertion_1 {
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
}

ex-kb:Assertion_2 {
    ex-kb:Workflow sio:hasPart ex-kb:Workflow .
}
# ------- Object Property Reflexivity  ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Reflexivity Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Reflexivity Back Tracer')), self.app.db)

    def test_object_property_irreflexivity_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Irreflexivity  -------
ex-kb:Assertion_1 {
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

    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
    #    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    sio:MathematicalEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:InformationContentEntity ;
        rdfs:label "mathematical entity" ;
        dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .

    sio:Set rdf:type owl:Class ;
        rdfs:subClassOf sio:MathematicalEntity ;
        rdfs:label "set" ;
        dct:description "A set is a collection of entities, for which there may be zero members." .

    sio:Collection rdf:type owl:Class ;
        rdfs:subClassOf sio:Set ;
        rdfs:label "collection" ;
        dct:description "A collection is a set for which there exists at least one member, although any member need not to exist at any point in the collection's existence." .

    ex-kb:Group rdf:type sio:Collection ;
        rdfs:label "group" ;
        sio:hasMember ex-kb:Group .
}

ex-kb:Assertion_2 {
    ex-kb:Group rdf:type owl:Nothing .
}
# ------- Object Property Irreflexivity  ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Irreflexivity Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Irreflexivity Back Tracer')), self.app.db)

    def test_functional_object_property_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Functional Object Property -------
ex-kb:Assertion_1 {
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

    ex-kb:Tutor rdf:type sio:Human ;
        rdfs:label "tutor" .

    ex-kb:Teacher rdf:type sio:Human ;
        rdfs:label "teacher" .

    ex-kb:TeachingRole rdf:type sio:Role ;
        rdfs:label "teaching role" ;
        sio:isRoleOf ex-kb:Teacher , ex-kb:Tutor .
}

ex-kb:Assertion_2 {
    ex-kb:Teacher owl:sameAs ex-kb:Tutor .
}
# ------- Functional Object Property ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Functional Object Property Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Functional Object Property Back Tracer')), self.app.db)

    def test_property_domain_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Property Domain -------   
ex-kb:Assertion_1 {
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

    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

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

    sio:HeterogeneousSubstance  rdf:type owl:Class ;
        rdfs:label "heterogeneous substance" ;
        rdfs:subClassOf sio:MaterialEntity ;
        rdfs:subClassOf sio:ChemicalEntity ;
    #    <owl:disjointWith rdf:resource="http://semanticscience.org/resource/HomogeneousSubstance"/>
        dct:description "A heterogeneous substance is a chemical substance that is composed of more than one different kind of component." .

    sio:BiologicalEntity  rdf:type owl:Class ;
        rdfs:label "biological entity" ;
        rdfs:subClassOf sio:HeterogeneousSubstance ;
        dct:description "A biological entity is a heterogeneous substance that contains genomic material or is the product of a biological process." .

    sio:Organism rdf:type owl:Class ;
        owl:equivalentClass 
            [   rdf:type owl:Class ;
                owl:unionOf ( sio:CellularOrganism sio:Non-cellularOrganism ) ] ;
        rdfs:subClassOf sio:BiologicalEntity ;
        dct:description "A biological organisn is a biological entity that consists of one or more cells and is capable of genomic replication (independently or not)." ;
        rdfs:label "organism" .

    sio:CellularOrganism  rdf:type owl:Class ;
        rdfs:label "cellular organism" ;
        rdfs:subClassOf sio:Organism ;
    #    <owl:disjointWith rdf:resource="http://semanticscience.org/resource/Non-cellularOrganism"/>
        dct:description "A cellular organism is an organism that contains one or more cells." .

    sio:MulticellularOrganism  rdf:type owl:Class ;
        rdfs:label "multicellular organism" ;
        rdfs:subClassOf sio:CellularOrganism ;
        dct:description "A multi-cellular organism is an organism that consists of more than one cell." .

    sio:Human  rdf:type owl:Class ;
        rdfs:label "human" ;
        rdfs:subClassOf sio:MulticellularOrganism ;
        dct:description "A human is a primates of the family Hominidae and are characterized by having a large brain relative to body size, with a well developed neocortex, prefrontal cortex and temporal lobes, making them capable of abstract reasoning, language, introspection, problem solving and culture through social learning." .

    ex-kb:Mother rdf:type owl:Individual ;
        rdfs:label "mother" ;
        sio:isRoleOf ex-kb:Sarah ;
        sio:inRelationTo ex-kb:Tim .

    ex-kb:Sarah rdf:type sio:Human ;
        rdfs:label "Sarah" .

    ex-kb:Tim rdf:type sio:Human ;
        rdfs:label "Tim" .
}

ex-kb:Assertion_2 {
    ex-kb:Mother rdf:type sio:Role .
}
# ------- Property Domain ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Property Domain Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Property Domain Back Tracer')), self.app.db)

    def test_property_range_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Property Range -------
ex-kb:Assertion_1 {
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
}

ex-kb:Assertion_2 {
    ex-kb:Meter rdf:type sio:UnitOfMeasurement .
}
# ------- Property Range ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Property Range Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Property Range Back Tracer')), self.app.db)

    def test_inverse_functional_object_property_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Inverse Functional Object Property -------
ex-kb:Assertion_1 {
    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    sio:hasProperty rdf:type owl:ObjectProperty ,
                                    owl:InverseFunctionalProperty;
        rdfs:label "has property" ;
        owl:inverseOf sio:isPropertyOf ;
        dct:description "has property is a relation between an entity and the quality, capability or role that it and it alone bears." ;
        rdfs:subPropertyOf sio:hasAttribute .

    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    sio:Representation rdf:type owl:Class ;
        rdfs:subClassOf sio:InformationContentEntity ;
        dct:description "A representation is a entity that in some way represents another entity (or attribute thereof)." ;
        rdfs:label "representation" .

    sio:Symbol rdf:type owl:Class ;
        rdfs:subClassOf sio:Representation ;
        dct:description "A symbol is a proposition about what an entity represents." ;
        rdfs:label "symbol" .

    ex:MolecularFormula rdfs:subClassOf sio:Symbol ;
        rdfs:label "molecular formula" .

    ex-kb:Water sio:hasProperty ex-kb:H2O ;
        rdfs:label "water" .

    ex-kb:HyrdogenDioxide sio:hasProperty ex-kb:H2O ;
        rdfs:label "hydrogen dioxide" .

    ex-kb:H2O rdf:type ex:MolecularFormula ;
        rdfs:label "H2O" .
}

ex-kb:Assertion_2 {
    ex-kb:Water owl:sameAs ex-kb:HyrdogenDioxide .
}
# ------- Inverse Functional Object Property ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Inverse Functional Object Property Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Inverse Functional Object Property Back Tracer')), self.app.db)

    def test_functional_data_property_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Functional Data Property -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex-kb:HeightOfTom sio:hasValue "5"^^xsd:integer .
    ex-kb:HeightOfTom sio:hasValue "6"^^xsd:integer .
}

ex-kb:Assertion_2 {
    ex-kb:HeightOfTom rdf:type owl:Nothing .
}
# ------- Functional Data Property ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Functional Data Property Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Functional Data Property Back Tracer')), self.app.db)

    def test_property_disjointness_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Property Disjointness -------
ex-kb:Assertion_1 {
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
}

ex-kb:Assertion_2 {
    ex-kb:Susan rdf:type owl:Nothing .
}
# ------- Property Disjointness ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Property Disjointness Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Property Disjointness Back Tracer')), self.app.db)

    def test_object_property_symmetry_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Symmetry -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    ex-kb:Peter rdf:type sio:Human ;
        rdfs:label "Peter" ;
        sio:isRelatedTo ex-kb:Samantha .

    ex-kb:Samantha rdf:type sio:Human ;
        rdfs:label "Samantha" .
}

ex-kb:Assertion_2 {
    ex-kb:Samantha sio:isRelatedTo ex-kb:Peter .
}
# ------- Object Property Symmetry ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Symmetry Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Symmetry Back Tracer')), self.app.db)

    def test_object_property_asymmetry_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Asymmetry -------
ex-kb:Assertion_1 {
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
}

ex-kb:Assertion_2 {
    ex-kb:Face rdf:type owl:Nothing .
}
# ------- Object Property Asymmetry ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Asymmetry Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Asymmetry Back Tracer')), self.app.db)

    def test_class_inclusion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Inclusion ------- 
ex-kb:Assertion_1 {
    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

    sio:MaterialEntity  rdf:type owl:Class ;
        rdfs:label "material entity" ;
        rdfs:subClassOf sio:Object ;
    #    <rdfs:subClassOf rdf:nodeID="arc0158b11"/>
    #    <rdfs:subClassOf rdf:nodeID="arc0158b12"/>
        dct:description "A material entity is a physical entity that is spatially extended, exists as a whole at any point in time and has mass." .
}

ex-kb:Assertion_2 {
    sio:MaterialEntity rdfs:subClassOf sio:Entity .
}
# ------- Class Inclusion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Class Inclusion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Class Inclusion Back Tracer')), self.app.db)

    def test_object_property_inclusion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Inclusion -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    sio:hasProperty rdf:type owl:ObjectProperty ,
                                    owl:InverseFunctionalProperty;
        rdfs:label "has property" ;
        owl:inverseOf sio:isPropertyOf ;
        dct:description "has property is a relation between an entity and the quality, capability or role that it and it alone bears." ;
        rdfs:subPropertyOf sio:hasAttribute .
    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

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

    sio:MathematicalEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:InformationContentEntity ;
        rdfs:label "mathematical entity" ;
        dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .

    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
    #    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    ex-kb:Samantha sio:hasProperty ex-kb:AgeOfSamantha .

    ex-kb:AgeOfSamantha rdf:type sio:Age ;
        rdfs:label "Samantha's age" .
}

ex-kb:Assertion_2 {
    ex-kb:Samantha sio:hasAttribute ex-kb:AgeOfSamantha .
}
# ------- Object Property Inclusion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Inclusion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Inclusion Back Tracer')), self.app.db)

    def test_data_property_inclusion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Inclusion -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex-kb:AgeOfSamantha rdf:type sio:Age ;
        rdfs:label "Samantha's age" .

    ex:hasExactValue rdf:type owl:DatatypeProperty ;
        rdfs:label "has exact value" ;
        rdfs:subPropertyOf sio:hasValue .

    ex-kb:AgeOfSamantha ex:hasExactValue "25.82"^^xsd:decimal .
}

ex-kb:Assertion_2 {
    ex-kb:AgeOfSamantha sio:hasValue "25.82"^^xsd:decimal .
}
# ------- Data Property Inclusion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Property Inclusion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Property Inclusion Back Tracer')), self.app.db)

    def test_property_chain_inclusion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Chain Inclusion -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    sio:isSpatiotemporallyRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:subPropertyOf sio:isRelatedTo ;
        rdfs:label "is spatiotemporally related to" ;
        dct:description "A is spatiotemporally related to B iff A is in the spatial or temporal vicinity of B" .

    sio:overlapsWith rdf:type owl:ObjectProperty ,
            owl:SymmetricProperty ,
            owl:ReflexiveProperty ;
        rdfs:subPropertyOf sio:isSpatiotemporallyRelatedTo ;
        owl:propertyChainAxiom ( sio:overlapsWith sio:isPartOf ) ;
        dct:description "A overlaps with B iff there is some C that is part of both A and B." ;
        rdfs:label "overlaps with" .

    ex-kb:Rug rdf:type sio:Object ;
        rdfs:label "rug" ;
        sio:overlapsWith ex-kb:FloorPanel .

    ex-kb:FloorPanel rdf:type sio:Object ;
        rdfs:label "floor panel" ;
        sio:isPartOf ex-kb:Floor .

    ex-kb:Floor rdf:type sio:Object ;
        rdfs:label "floor" .
}

ex-kb:Assertion_2 {
    ex-kb:Rug sio:overlapsWith ex-kb:Floor .
}
# ------- Object Property Chain Inclusion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Chain Inclusion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Chain Back Tracer')), self.app.db)

    def test_class_equivalence_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Equivalence -------
ex-kb:Assertion_1 {
    ex:Fake rdf:type owl:Class ;
        owl:equivalentClass sio:Fictional ;
        rdfs:label "fake" .

    ex-kb:Hubert rdf:type ex:Fake ;
        rdfs:label "Hubert" .
}

ex-kb:Assertion_2 {
    ex-kb:Hubert rdf:type sio:Fictional .
}
# ------- Class Equivalence ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Class Equivalence Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Class Equivalence Back Tracer')), self.app.db)

    def test_property_equivalence_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Property Equivalence -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex-kb:AgeOfSamantha rdf:type sio:Age ;
        rdfs:label "Samantha's age" ;
        sio:hasValue "25.82"^^xsd:decimal .

    ex:hasValue rdf:type owl:DatatypeProperty ;
        rdfs:label "has value" ;
        owl:equivalentProperty sio:hasValue .
}

ex-kb:Assertion_2 {
    ex-kb:AgeOfSamantha ex:hasValue "25.82"^^xsd:decimal .
}
# ------- Property Equivalence ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Property Equivalence Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Property Equivalence Back Tracer')), self.app.db)

    def test_individual_inclusion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Individual Inclusion -------
ex-kb:Assertion_1 {
    sio:Role rdf:type owl:Class ;
        rdfs:label "role" ;
        rdfs:subClassOf sio:RealizableEntity ;
        dct:description "A role is a realizable entity that describes behaviours, rights and obligations of an entity in some particular circumstance." .

    ex-kb:Farmer rdf:type sio:Role ;
        rdfs:label "farmer" .
}

ex-kb:Assertion_2 {
    ex-kb:Farmer rdf:type sio:RealizableEntity .
}
# ------- Individual Inclusion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Individual Inclusion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Individual Inclusion Back Tracer')), self.app.db)

    def test_object_property_inversion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Inversion -------
ex-kb:Assertion_1 {
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
}

ex-kb:Assertion_2 {
    ex-kb:Finger sio:hasPart ex-kb:Fingernail .
}
# ------- Object Property Inversion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Inversion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Inversion Back Tracer')), self.app.db)

    def test_same_individual_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Same Individual -------
ex-kb:Assertion_1 {
    ex-kb:Peter rdf:type sio:Human ;
        rdfs:label "Peter" ;
        sio:isRelatedTo ex-kb:Samantha .

    ex-kb:Samantha rdf:type sio:Human ;
        rdfs:label "Samantha" .

    ex-kb:Peter owl:sameAs ex-kb:Pete .
}

ex-kb:Assertion_2 {
    ex-kb:Pete rdf:type sio:Human ;
        rdfs:label "Peter" ;
        sio:isRelatedTo ex-kb:Samantha .
}
# -------  Same Individual ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Same Individual Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Same Individual Back Tracer')), self.app.db)

    def test_different_individuals_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Different Individuals ------- 
ex-kb:Assertion_1 {
    ex-kb:Sam owl:differentFrom ex-kb:Samantha .
    ex-kb:Sam owl:sameAs ex-kb:Samantha .
}

ex-kb:Assertion_2 {
    ex-kb:Sam rdf:type owl:Nothing .
}
# -------  Different Individuals ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Different Individuals Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Different Individuals Back Tracer')), self.app.db)


    def test_class_assertion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Class Assertion -------
ex-kb:Assertion_1 {
    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Attribute rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "attribute" ;
        dct:description "An attribute is a characteristic of some entity." .

    sio:RealizableEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Attribute ;
        dct:description "A realizable entity is an attribute that is exhibited under some condition and is realized in some process." ;
        rdfs:label "realizable entity" .

    sio:Quality rdf:type owl:Class ;
        rdfs:subClassOf sio:Attribute ;
        owl:disjointWith sio:RealizableEntity ;
        dct:description "A quality is an attribute that is intrinsically associated with its bearer (or its parts), but whose presence/absence and observed/measured value may vary." ;
        rdfs:label "quality" .

    ex-kb:Reliable rdf:type sio:Quality ;
        rdfs:label "reliable" .
}

ex-kb:Assertion_2 {
    ex-kb:Reliable rdf:type sio:Attribute , sio:Entity .
}
# -------  Class Assertion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Class Assertion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Class Assertion Back Tracer')), self.app.db)

#    def test_positive_object_property_assertion_back_tracer(self):
#        self.dry_run = False
#
#        np = nanopub.Nanopublication()
#        np.assertion.parse(data=prefixes+'''
## <-------  Positive Object Property Assertion ------- 
## Need to come back to this
#
#?resource ?objectProperty ?o.
#?objectProperty rdf:type owl:ObjectProperty .
#?class rdf:type owl:Class;
#    rdfs:subClassOf|owl:equivalentClass
#        [ rdf:type owl:Restriction ;
#            owl:onProperty ?objectProperty ;
#            owl:someValuesFrom owl:Thing ] .
## -------  Positive Object Property Assertion -------> 
#''', format="trig")
#        self.app.nanopub_manager.publish(*[np])
#        agent =  config.Config["inferencers"]["Positive Object Property Assertion"]
#        agent.process_graph(self.app.db)
#        self.assertIn((KB.ReplaceMe, RDF.type, OWL.Nothing), self.app.db)
#
#    def test_positive_data_property_assertion_back_tracer(self):
#        self.dry_run = False
#
#        np = nanopub.Nanopublication()
#        np.assertion.parse(data=prefixes+'''
## <------- Positive Data Property Assertion ------- 
## Need to come back to this
# -------  Positive Data Property Assertion -------> 
#''', format="trig")
#        self.app.nanopub_manager.publish(*[np])
#        agent =  config.Config["inferencers"]["Positive Data Property Assertion"]
#        agent.process_graph(self.app.db)
#        self.assertIn((KB.ReplaceMe, RDF.type, OWL.Nothing), self.app.db)

    def test_negative_object_property_assertion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Negative Object Property Assertion -------
ex-kb:Assertion_1 {
    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    sio:hasUnit rdf:type owl:ObjectProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has unit" ;
        owl:inverseOf sio:isUnitOf ;
        rdfs:range sio:UnitOfMeasurement ;
        rdfs:subPropertyOf sio:hasAttribute ;
        dct:description "has unit is a relation between a quantity and the unit it is a multiple of." .

    ex-kb:AgeOfSamantha rdf:type sio:Age ;
        rdfs:label "Samantha's age" .

    ex-kb:NOPA rdf:type owl:NegativePropertyAssertion ; 
        owl:sourceIndividual ex-kb:AgeOfSamantha ; 
        owl:assertionProperty sio:hasUnit ; 
        owl:targetIndividual ex-kb:Meter .

    ex-kb:AgeOfSamantha sio:hasUnit ex-kb:Meter .
}

ex-kb:Assertion_2 {
    ex-kb:AgeOfSamantha rdf:type owl:Nothing .
}
# -------  Negative Object Property Assertion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Negative Object Property Assertion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Negative Object Property Assertion Back Tracer')), self.app.db)

    def test_negative_data_property_assertion_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Negative DataPropertyAssertion -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex-kb:NDPA rdf:type owl:NegativePropertyAssertion ; 
        owl:sourceIndividual ex-kb:AgeOfPeter ; 
        owl:assertionProperty sio:hasValue ; 
        owl:targetValue "10" .

    ex-kb:AgeOfPeter rdf:type sio:Age;
        rdfs:label "Peter's age" ;
        sio:hasValue "10" .
}

ex-kb:Assertion_2 {
    ex-kb:AgeOfPeter rdf:type owl:Nothing .
}
# -------  Negative DataProperty Assertion ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Negative Data Property Assertion Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Negative Data Property Assertion Back Tracer')), self.app.db)

    def test_keys_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Keys -------
ex-kb:Assertion_1 {
    ex:uniqueID rdf:type owl:DatatypeProperty ;
        rdfs:label "unique identifier" .

    ex:Person rdf:type owl:Class ;
        rdfs:subClassOf sio:Human ;
        rdfs:label "person" ;
        owl:hasKey ( ex:uniqueID ) .

    ex-kb:John rdf:type ex:Person ;
        rdfs:label "John" ;
        ex:uniqueID "101D" .

    ex-kb:Jack rdf:type ex:Person ;
        rdfs:label "Jack" ;
        ex:uniqueID "101D" .
}

ex-kb:Assertion_2 {
    ex-kb:John owl:sameAs ex-kb:Jack .
}
# ------- Keys ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Keys Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Keys Back Tracer')), self.app.db)

    def test_object_some_values_from_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Some Values From -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    sio:hasMember rdf:type owl:ObjectProperty ,
                                    owl:IrreflexiveProperty ;
        rdfs:subPropertyOf sio:hasAttribute ;
        owl:inverseOf sio:isMemberOf ;
        rdfs:label "has member" ;
        dct:description "has member is a mereological relation between a collection and an item." .

    sio:CollectionOf3dMolecularStructureModels rdf:type owl:Class ;
        rdfs:subClassOf sio:Collection ,
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasMember ;
                owl:someValuesFrom sio:3dStructureModel ] ;
        rdfs:label "collection of 3d molecular structure models" ;
        dct:description "A collection of 3D molecular structure models is just that." .

    sio:3dStructureModel rdf:type owl:Class ;
        rdfs:subClassOf sio:TertiaryStructureDescriptor ;
        rdfs:label "3d structure model" ;
        dct:description "A 3D structure model is a representation of the spatial arrangement of one or more chemical entities." .

    sio:TertiaryStructureDescriptor rdf:type owl:Class ;
        rdfs:subClassOf sio:BiomolecularStructureDescriptor ;
        rdfs:label "tertiary structure descriptor" ;
        dct:description "A tertiary structure descriptor describes 3D topological patterns in a biopolymer." .

    sio:BiomolecularStructureDescriptor rdf:type owl:Class ;
        rdfs:subClassOf sio:MolecularStructureDescriptor ;
        rdfs:label "biomolecular structure descriptor" ;
        dct:description "A biomolecular structure descriptor is structure description for organic compounds." .

    sio:MolecularStructureDescriptor rdf:type owl:Class ;
        rdfs:subClassOf sio:ChemicalQuality ;
    #    <rdfs:subClassOf rdf:nodeID="arc0158b921"/>
    #    <rdfs:subClassOf rdf:nodeID="arc0158b922"/>
        rdfs:label "molecular structure descriptor" ;
        dct:description "A molecular structure descriptor is data that describes some aspect of the molecular structure (composition) and is about some chemical entity." .

    sio:ChemicalQuality rdf:type owl:Class ;
        rdfs:subClassOf sio:ObjectQuality ;
        rdfs:label "chemical quality" ;
        dct:description "Chemical quality is the quality of a chemical entity." .

    sio:ObjectQuality rdf:type owl:Class ;
        rdfs:subClassOf sio:Quality ;
        rdfs:label "object quality" ;
        dct:description "An object quality is quality of an object." .

    ex-kb:MolecularCollection rdf:type owl:Individual ;
        rdfs:label "molecular collection" ;
        sio:hasMember ex-kb:WaterMolecule .

    ex-kb:WaterMolecule rdf:type sio:3dStructureModel  .
}

ex-kb:Assertion_2 {
    ex-kb:MolecularCollection rdf:type sio:CollectionOf3dMolecularStructureModels .
}
# -------  Object Some Values From ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Some Values From Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Some Values From Back Tracer')), self.app.db)

    def test_data_some_values_from_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Some Values From -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex:Text rdf:type owl:Class ;
        rdfs:subClassOf
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasValue  ;
                owl:someValuesFrom xsd:string ] .

    ex-kb:Question rdf:type ex:Text ;
        sio:hasValue "4"^^xsd:integer .
}

ex-kb:Assertion_2 {
    ex-kb:Question rdf:type owl:Nothing .
}
# -------  Data Some Values From ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Some Values From Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Some Values From Back Tracer')), self.app.db)

    def test_object_has_self_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Has Self -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    ex:SelfAttributing rdf:type owl:Class ;
        rdfs:subClassOf 
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasAttribute ;
                owl:hasSelf "true"^^xsd:boolean ] .

    ex-kb:Blue rdf:type ex:SelfAttributing .
}

ex-kb:Assertion_2 {
    ex-kb:Blue sio:hasAttribute ex-kb:Blue .
}
# -------  Object Has Self ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Has Self Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Has Self Back Tracer')), self.app.db)

    def test_object_has_value_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Has Value -------
ex-kb:Assertion_1 {
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

    ex:Vehicle rdf:type owl:Class ;
        rdfs:subClassOf 
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasPart ;
                owl:hasValue ex-kb:Wheel ] .

    ex-kb:Car rdf:type ex:Vehicle ;
        sio:hasPart ex-kb:Mirror .

    ex-kb:Mirror owl:differentFrom ex-kb:Wheel .
}

ex-kb:Assertion_2 {
    ex-kb:Car sio:hasPart ex-kb:Wheel .
}
# -------  Object Has Value ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Has Value Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Has Value Back Tracer')), self.app.db)

    def test_data_has_value_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Has Value -------
ex-kb:Assertion_1 {
    ex:Unliked rdf:type owl:Class ;
        owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ex:hasAge ;
                owl:hasValue "23"^^xsd:integer ] .

    ex-kb:Tom ex:hasAge "23"^^xsd:integer .
}

ex-kb:Assertion_2 {
    ex-kb:Tom rdf:type ex:Unliked .
}
# -------  Data Has Value ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Has Value Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Has Value Back Tracer')), self.app.db)

    def test_all_disjoint_classes_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  All Disjoint Classes-------
ex-kb:Assertion_1 {
    sio:Entity rdf:type owl:Class ;
        rdfs:label "entity" ;
        dct:description "Every thing is an entity." .

    sio:Process rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
    #    <rdfs:subClassOf rdf:nodeID="arc0158b17"/>
    #    <rdfs:subClassOf rdf:nodeID="arc0158b18"/>
        dct:description "A process is an entity that is identifiable only through the unfolding of time, has temporal parts, and unless otherwise specified/predicted, cannot be identified from any instant of time in which it exists." ;
        rdfs:label "process" .

    sio:Attribute rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "attribute" ;
        dct:description "An attribute is a characteristic of some entity." .

    sio:Object rdf:type owl:Class ;
        rdfs:subClassOf sio:Entity ;
        rdfs:label "object" ;
        #<rdfs:subClassOf rdf:nodeID="arc703eb381"/>
        dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

    ex-kb:DisjointClassesRestriction rdf:type owl:AllDisjointClasses ;
        owl:members ( sio:Process sio:Attribute sio:Object ) .
}

ex-kb:Assertion_2 {
    sio:Process owl:disjointWith sio:Attribute , sio:Object .
    sio:Attribute owl:disjointWith sio:Process , sio:Object .
    sio:Object owl:disjointWith sio:Process , sio:Attribute .
}
# -------  All Disjoint Classes ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Disjoint Classes Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('All Disjoint Classes Back Tracer')), self.app.db)

    def test_all_disjoint_properties_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  All Disjoint Properties-------
ex-kb:Assertion_1 {
    ex-kb:DisjointPropertiesRestriction rdf:type owl:AllDisjointProperties ;
        owl:members ( ex:hasMother ex:hasFather ex:hasSibling ) .

    ex:hasMother rdf:type owl:ObjectProperty ;
        rdfs:label "has mother" .

    ex:hasFather rdf:type owl:ObjectProperty ;
        rdfs:label "has father" .

    ex:hasSibling rdf:type owl:ObjectProperty ;
        rdfs:label "has sibling" .
}

ex-kb:Assertion_2 {
    ex:hasMother owl:propertyDisjointWith ex:hasFather , ex:hasSibling .
    ex:hasFather owl:propertyDisjointWith ex:hasMother , ex:hasSibling .
    ex:hasSibling owl:propertyDisjointWith ex:hasMother, ex:hasFather .
}
# -------  All Disjoint Properties ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Disjoint Properties Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('All Disjoint Properties Back Tracer')), self.app.db)

    def test_all_different_individuals_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  All Different Individuals-------
ex-kb:Assertion_1 {
    ex-kb:DistinctTypesRestriction rdf:type owl:AllDifferent ;
        owl:distinctMembers
            ( ex-kb:Integer
            ex-kb:String 
            ex-kb:Boolean
            ex-kb:Double 
            ex-kb:Float 
            ex-kb:Tuple 
            ) .
}

ex-kb:Assertion_2 {
    ex-kb:Integer owl:differentFrom ex-kb:String , ex-kb:Boolean, ex-kb:Double , ex-kb:Float , ex-kb:Tuple .
    ex-kb:String owl:differentFrom ex-kb:Integer , ex-kb:Boolean, ex-kb:Double, ex-kb:Float , ex-kb:Tuple .
    ex-kb:Boolean owl:differentFrom ex-kb:Integer , ex-kb:String, ex-kb:Double, ex-kb:Float , ex-kb:Tuple .
    ex-kb:Double owl:differentFrom ex-kb:Integer , ex-kb:String , ex-kb:Boolean, ex-kb:Float , ex-kb:Tuple .
    ex-kb:Float owl:differentFrom ex-kb:Integer , ex-kb:String , ex-kb:Boolean, ex-kb:Double , ex-kb:Tuple .
    ex-kb:Tuple owl:differentFrom ex-kb:Integer , ex-kb:String , ex-kb:Boolean, ex-kb:Double, ex-kb:Float .
}
# -------  All Different Individuals------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Different Individuals Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('All Different Individuals Back Tracer')), self.app.db)

    def test_object_one_of_membership_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object One Of -------
ex-kb:Assertion_1 {
    ex:Type rdf:type owl:Class ;
        owl:oneOf (ex-kb:Integer ex-kb:String ex-kb:Boolean ex-kb:Double ex-kb:Float) .

    ex-kb:DistinctTypesRestriction rdf:type owl:AllDifferent ;
        owl:distinctMembers
            ( ex-kb:Integer
            ex-kb:String 
            ex-kb:Boolean
            ex-kb:Double 
            ex-kb:Float 
            ex-kb:Tuple 
            ) .
}

ex-kb:Assertion_2 {
    ex-kb:Tuple rdf:type ex:Type .
    ex-kb:Integer rdf:type ex:Type .
    ex-kb:String rdf:type ex:Type .
    ex-kb:Boolean rdf:type ex:Type .
    ex-kb:Double rdf:type ex:Type .
    ex-kb:Float rdf:type ex:Type .
}
# -------  Object One Of Membership ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Different Individuals Back Tracer"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object One Of Membership Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object One Of Membership Back Tracer')), self.app.db)

    def test_object_one_of_inconsistency_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object One Of Inconsistency-------
ex-kb:Assertion_1 {
    ex:Type rdf:type owl:Class ;
        owl:oneOf (ex-kb:Integer ex-kb:String ex-kb:Boolean ex-kb:Double ex-kb:Float) .

    ex-kb:DistinctTypesRestriction rdf:type owl:AllDifferent ;
        owl:distinctMembers
            ( ex-kb:Integer
            ex-kb:String 
            ex-kb:Boolean
            ex-kb:Double 
            ex-kb:Float 
            ex-kb:Tuple 
            ) .

    ex-kb:Tuple rdf:type ex:Type .
}

ex-kb:Assertion_2 {
    ex-kb:Tuple rdf:type owl:Nothing .
}
# -------  Object One Of Inconsistency ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Different Individuals"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object One Of Inconsistency Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object One Of Inconsistency Back Tracer')), self.app.db)

    def test_data_one_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data One Of -------
ex-kb:Assertion_1 {
    ex:hasTeenAge rdf:type owl:DatatypeProperty ;
        rdfs:label "has age" ;
        rdfs:range [ rdf:type owl:DataRange ;
            owl:oneOf ("13"^^xsd:integer "14"^^xsd:integer "15"^^xsd:integer "16"^^xsd:integer "17"^^xsd:integer "18"^^xsd:integer "19"^^xsd:integer )].

    ex-kb:Sarah ex:hasTeenAge "12"^^xsd:integer .
    # Note that we need to update range rule to account for data ranges
}

ex-kb:Assertion_2 {
    ex-kb:Sarah rdf:type owl:Nothing .
}
# -------  Data One Of ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data One Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data One Of Back Tracer')), self.app.db)

    def test_datatype_restriction_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Datatype Restriction -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    sio:ProbabilityMeasure rdf:type owl:Class ;
        rdfs:subClassOf sio:DimensionlessQuantity ;
        dct:description "A probability measure is quantity of how likely it is that some event will occur." ;
        rdfs:label "probability measure" .

    sio:ProbabilityValue rdf:type owl:Class ;
        rdfs:subClassOf sio:ProbabilityMeasure ;
        rdfs:subClassOf
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasValue ;
                owl:someValuesFrom 
                    [ rdf:type rdfs:Datatype ;
                        owl:onDatatype xsd:double ;
                        owl:withRestrictions ( [ xsd:minInclusive "0.0"^^xsd:double ] [ xsd:maxInclusive "1.0"^^xsd:double ] ) 
                    ]
            ] ;
        dct:description "A p-value or probability value is the probability of obtaining a test statistic at least as extreme as the one that was actually observed, assuming that the null hypothesis is true" ;
        #<sio:hasSynonym xml:lang="en">p-value</sio:hasSynonym>
        rdfs:label "probability value" .

    ex-kb:EffortExerted rdf:type sio:ProbabilityValue ;
        rdfs:label "effort exerted" ;
        sio:hasValue "1.1"^^xsd:double .
}

ex-kb:Assertion_2 {
    ex-kb:EffortExerted rdf:type owl:Nothing .
}
# ------- Datatype Restriction ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Datatype Restriction Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Datatype Restriction Back Tracer')), self.app.db)

    def test_object_all_values_from_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object All Values From -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    sio:hasMember rdf:type owl:ObjectProperty ,
                                    owl:IrreflexiveProperty ;
        rdfs:subPropertyOf sio:hasAttribute ;
        owl:inverseOf sio:isMemberOf ;
        rdfs:label "has member" ;
        dct:description "has member is a mereological relation between a collection and an item." .

    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
    #    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    sio:ComputationalEntity rdf:type owl:Class;
        rdfs:subClassOf sio:InformationContentEntity ;
        rdfs:label "computational entity" ;
        dct:description "A computational entity is an information content entity operated on using some computational system." .

    sio:Namespace rdf:type owl:Class ;
        rdfs:subClassOf sio:ComputationalEntity ,
            [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasMember ;
            owl:allValuesFrom sio:Identifier ] ;
        rdfs:label "namespace" ;
        dct:description "A namespace is an informational entity that defines a logical container for a set of symbols or identifiers." .

    ex-kb:NamespaceInstance rdf:type sio:Namespace ;
        sio:hasMember ex-kb:NamespaceID .
}

ex-kb:Assertion_2 {
    ex-kb:NamespaceID rdf:type sio:Identifier .
}
# -------  Object All Values From ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object All Values From Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object All Values From Back Tracer')), self.app.db)

    def test_data_all_values_from_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data All Values From -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex:Integer rdf:type owl:Class ;
        rdfs:subClassOf sio:ComputationalEntity ,
            [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasValue ;
            owl:allValuesFrom xsd:integer ] ;
        rdfs:label "integer" .

    ex-kb:Ten rdf:type ex:Integer ;
        sio:hasValue "ten"^^xsd:string .
}

ex-kb:Assertion_2 {
    ex-kb:Ten rdf:type owl:Nothing .
}
# -------  Data All Values From ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data All Values From Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data All Values From Back Tracer')), self.app.db)

    def test_object_max_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Max Cardinality -------
ex-kb:Assertion_1 {
    sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                    owl:SymmetricProperty ;
        rdfs:label "is related to" ;
        dct:description "A is related to B iff there is some relation between A and B." .

    sio:hasAttribute rdf:type owl:ObjectProperty ;
        rdfs:label "has attribute" ;
        dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
        rdfs:subPropertyOf sio:isRelatedTo .

    sio:hasMember rdf:type owl:ObjectProperty ,
                                    owl:IrreflexiveProperty ;
        rdfs:subPropertyOf sio:hasAttribute ;
        owl:inverseOf sio:isMemberOf ;
        rdfs:label "has member" ;
        dct:description "has member is a mereological relation between a collection and an item." .

    ex:DeadlySins rdf:type owl:Class ;
        rdfs:subClassOf sio:Collection ;
        rdfs:subClassOf 
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasMember ;
                owl:maxCardinality "7"^^xsd:integer ] ;
        rdfs:label "seven deadly sins" .

    ex-kb:SevenDeadlySins rdf:type ex:DeadlySins ;
        sio:hasMember 
            ex-kb:Pride ,
            ex-kb:Envy ,
            ex-kb:Gluttony ,
            ex-kb:Greed ,
            ex-kb:Lust ,
            ex-kb:Sloth ,
            ex-kb:Wrath ,
            ex-kb:Redundancy .

    ex-kb:DistinctSinsRestriction rdf:type owl:AllDifferent ;
        owl:distinctMembers
            (ex-kb:Pride 
            ex-kb:Envy 
            ex-kb:Gluttony 
            ex-kb:Greed 
            ex-kb:Lust 
            ex-kb:Sloth 
            ex-kb:Wrath 
            ex-kb:Redundancy ) .
}

ex-kb:Assertion_2 {
    ex-kb:SevenDeadlySins rdf:type owl:Nothing .
}
# -------  Object Max Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Different Individuals"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Max Cardinality Back Tracer')), self.app.db)

    def test_object_qualified_max_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Qualified Max Cardinality -------
ex-kb:Assertion_1 {
    sio:hasComponentPart rdf:type owl:ObjectProperty ;
        rdfs:subPropertyOf sio:hasDirectPart ;
        rdfs:label "has component part" ;
        dct:description "has component part is a relation between a whole and a component part where the component is instrinsic to the whole, and loss of the part would change the kind that it is." .

    sio:Triangle rdf:type owl:Class ;
        rdfs:subClassOf sio:Polygon ;
        dct:description "A triangle is a polygon composed of three points and three line segments, in which each point is fully connected to another point along through the line segment." ;
        rdfs:label "triangle" .

    sio:LineSegment rdf:type owl:Class ;
        rdfs:subClassOf sio:Line ;
    #    <rdfs:subClassOf rdf:nodeID="arc703eb252"/>
        dct:description "A line segment is a line and a part of a curve that is (inclusively) bounded by two terminal points." ;
        rdfs:label "line segment" .

    sio:DirectedLineSegment rdf:type owl:Class ;
        rdfs:subClassOf sio:LineSegment ;
    #    <rdfs:subClassOf rdf:nodeID="arc703eb253"/>
    #    <rdfs:subClassOf rdf:nodeID="arc703eb254"/>
        dct:description "A directed line segment is a line segment that is contained by an ordered pair of endpoints (a start point and an endpoint)." ;
        rdfs:label "directed line segment" .

    sio:ArrowedLineSegment rdf:type owl:Class ;
        rdfs:subClassOf sio:DirectedLineSegment ;
        rdfs:subClassOf 
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasPart ;
                owl:someValuesFrom sio:Triangle ] ;
        rdfs:subClassOf 
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:hasComponentPart ; 
                owl:onClass sio:Triangle ;
                owl:maxQualifiedCardinality "2"^^xsd:nonNegativeInteger ] ;
        dct:description "An arrowed line is a directed line segment in which one or both endpoints is tangentially part of a triangle that bisects the line." ;
        rdfs:label "arrowed line segment" .

    ex-kb:TripleArrowLineSegment rdf:type sio:ArrowedLineSegment ;
        rdfs:label "triple arrow line segment" ;
        sio:hasComponentPart
            ex-kb:LineSegment ,
            ex-kb:FirstArrow ,
            ex-kb:SecondArrow ,
            ex-kb:ThirdArrow .

    ex-kb:FirstArrow rdf:type sio:Triangle ;
        rdfs:label "first arrow" .

    ex-kb:SecondArrow rdf:type sio:Triangle ;
        rdfs:label "first arrow" .

    ex-kb:ThirdArrow rdf:type sio:Triangle ;
        rdfs:label "first arrow" .

    ex-kb:LineSegment rdf:type sio:LineSegment ;
        rdfs:label "line segment " .
}

ex-kb:Assertion_2 {
    ex-kb:TripleArrowLineSegment rdf:type owl:Nothing .
}
# -------  Object Qualified Max Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Qualified Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Qualified Max Cardinality Back Tracer')), self.app.db)

    def test_object_min_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# Need to come back to this to expand list size and make sure it still works
# <-------  Object Min Cardinality -------
sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                owl:SymmetricProperty ;
    rdfs:label "is related to" ;
    dct:description "A is related to B iff there is some relation between A and B." .

sio:hasAttribute rdf:type owl:ObjectProperty ;
    rdfs:label "has attribute" ;
    dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
    rdfs:subPropertyOf sio:isRelatedTo .

sio:hasMember rdf:type owl:ObjectProperty ,
                                owl:IrreflexiveProperty ;
    rdfs:subPropertyOf sio:hasAttribute ;
    owl:inverseOf sio:isMemberOf ;
    rdfs:label "has member" ;
    dct:description "has member is a mereological relation between a collection and an item." .

ex:StudyGroup rdf:type owl:Class ;
    rdfs:subClassOf sio:Collection ,
        [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasMember ;
            owl:minCardinality "2"^^xsd:integer ] ; 
    rdfs:label "study group" .

ex-kb:StudyGroupInstance rdf:type ex:StudyGroup ;
    sio:hasMember 
        ex-kb:Steve .#,
        #ex-kb:Luis ,
#        ex-kb:Ali .

ex-kb:Steve rdf:type sio:Human .
#ex-kb:Luis rdf:type sio:Human .
#ex-kb:Ali rdf:type sio:Human .

#ex-kb:DistinctStudentsRestriction rdf:type owl:AllDifferent ;
#    owl:distinctMembers
#        (ex-kb:Steve 
#        #ex-kb:Luis 
#        ex-kb:Ali ) .

# come back to abductive rule for this
# -------  Object Min Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Different Individuals"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object Min Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.StudyGroupInstance, SIO.hasMember))
        self.assertEquals(len(objects), 2)


    def test_object_qualified_min_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Qualified Min Cardinality -------
sio:hasComponentPart rdf:type owl:ObjectProperty ;
    rdfs:subPropertyOf sio:hasDirectPart ;
    rdfs:label "has component part" ;
    dct:description "has component part is a relation between a whole and a component part where the component is instrinsic to the whole, and loss of the part would change the kind that it is." .

sio:Polyline rdf:type owl:Class ;
    rdfs:subClassOf sio:GeometricEntity ;
    rdfs:subClassOf 
        [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasComponentPart ; 
            owl:minQualifiedCardinality "2"^^xsd:nonNegativeInteger ;
            owl:onClass sio:LineSegment ] ;
    dct:description "A polyline is a connected sequence of line segments." ;
    rdfs:label "polyline" .

sio:LineSegment rdf:type owl:Class ;
    rdfs:subClassOf sio:Line ;
#    <rdfs:subClassOf rdf:nodeID="arc703eb252"/>
    dct:description "A line segment is a line and a part of a curve that is (inclusively) bounded by two terminal points." ;
    rdfs:label "line segment" .

ex-kb:PolylineSegment rdf:type sio:Polyline ;
    rdfs:label "polyline segment " ;
    sio:hasComponentPart ex-kb:LineSegmentInstance .

ex-kb:LineSegmentInstance rdf:type sio:LineSegment ;
    rdfs:label "line segment instance" .

# come back to abductive rule for this
# -------  Object Qualified Min Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Qualified Min Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.PolylineSegment, SIO.hasComponentPart))
        self.assertEquals(len(objects), 2)

    def test_object_exact_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Exact Cardinality -------
sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                owl:SymmetricProperty ;
    rdfs:label "is related to" ;
    dct:description "A is related to B iff there is some relation between A and B." .

sio:hasAttribute rdf:type owl:ObjectProperty ;
    rdfs:label "has attribute" ;
    dct:description "has attribute is a relation that associates a entity with an attribute where an attribute is an intrinsic characteristic such as a quality, capability, disposition, function, or is an externally derived attribute determined from some descriptor (e.g. a quantity, position, label/identifier) either directly or indirectly through generalization of entities of the same type." ;
    rdfs:subPropertyOf sio:isRelatedTo .

sio:hasMember rdf:type owl:ObjectProperty ,
                                owl:IrreflexiveProperty ;
    rdfs:subPropertyOf sio:hasAttribute ;
    owl:inverseOf sio:isMemberOf ;
    rdfs:label "has member" ;
    dct:description "has member is a mereological relation between a collection and an item." .

ex:Duo rdf:type owl:Class ;
    rdfs:subClassOf 
        [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasMember ;
            owl:cardinality "2"^^xsd:integer
        ] .

ex-kb:Stooges rdf:type ex:Duo ;
    sio:hasMember 
        ex-kb:Larry ,
        ex-kb:Moe ,
        ex-kb:Curly .

ex-kb:DistinctStoogesRestriction rdf:type owl:AllDifferent ;
    owl:distinctMembers
        ( ex-kb:Larry 
        ex-kb:Moe 
        ex-kb:Curly ) .

ex-kb:BonnieAndClyde rdf:type ex:Duo ;
    rdfs:label "Bonnie and Clyde" ;
    sio:hasMember ex-kb:Bonnie .

ex-kb:Bonnie rdf:type sio:Human ;
    rdfs:label "Bonnie" .

# come back to abductive length check part of this rule
ex-kb:Stooges rdf:type owl:Nothing .
# -------  Object Exact Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Min Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.BonnieAndClyde, SIO.hasMember))
        self.assertEquals(len(objects), 2)
        agent =  config.Config["inferencers"]["Object Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Stooges, RDF.type, OWL.Nothing), self.app.db)

    def test_object_qualified_exact_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Qualified Exact Cardinality -------
sio:hasComponentPart rdf:type owl:ObjectProperty ;
    rdfs:subPropertyOf sio:hasDirectPart ;
    rdfs:label "has component part" ;
    dct:description "has component part is a relation between a whole and a component part where the component is instrinsic to the whole, and loss of the part would change the kind that it is." .

sio:PolygonEdge rdf:type owl:Class ;
    rdfs:subClassOf sio:LineSegment ;
    rdfs:subClassOf 
        [ rdf:type owl:Restriction ;
            owl:onProperty sio:isPartOf ;
            owl:someValuesFrom sio:Polygon ] ;
    rdfs:subClassOf 
        [ rdf:type owl:Restriction ;
            owl:onProperty sio:hasComponentPart ; 
            owl:onClass sio:PolygonVertex ;
            owl:qualifiedCardinality "2"^^xsd:nonNegativeInteger ] ;
    dct:description "A polygon edge is a line segment joining two polygon vertices." ;
    rdfs:label "polygon edge" .

ex-kb:TripleVertexPolyEdge rdf:type sio:PolygonEdge ;
    rdfs:label "triple vertex polygon edge" ;
    sio:hasComponentPart ex-kb:VertexOne , ex-kb:VertexTwo , ex-kb:VertexThree .

ex-kb:VertexOne rdf:type sio:PolygonVertex ;
    rdfs:label "vertex one" .

ex-kb:VertexTwo rdf:type sio:PolygonVertex ;
    rdfs:label "vertex two" .

ex-kb:VertexThree rdf:type sio:PolygonVertex ;
    rdfs:label "vertex three" .

ex-kb:SingleVertexPolyEdge rdf:type sio:PolygonEdge ;
    rdfs:label "triple vertexed polygon edge" ;
    sio:hasComponentPart ex-kb:VertexOne .

# come back to abductive length check part of this rule
ex-kb:TripleVertexPolyEdge rdf:type owl:Nothing .
# -------  Object Qualified Exact Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Qualified Min Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.SingleVertexPolyEdge, SIO.hasComponentPart))
        self.assertEquals(len(objects), 2)
        agent =  config.Config["inferencers"]["Object Qualified Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.TripleVertexPolyEdge, RDF.type, OWL.Nothing), self.app.db)

    def test_data_max_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Max Cardinality -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex:hasAge rdf:type owl:DatatypeProperty ;
        rdfs:label "has age" ;
        rdfs:subPropertyOf sio:hasValue .

    ex:Person rdf:type owl:Class ;
        rdfs:label "person" ;
        rdfs:subClassOf
            [ rdf:type owl:Restriction ;
                owl:onProperty ex:hasAge ;
                owl:maxCardinality "1"^^xsd:integer ] . 

    ex-kb:Katie rdf:type ex:Person ;
        rdfs:label "Katie" ;
        ex:hasAge "31"^^xsd:integer , "34"^^xsd:integer .
}

ex-kb:Assertion_2 {
    ex-kb:Katie rdf:type owl:Nothing .
}
# -------  Data Max Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Max Cardinality Back Tracer')), self.app.db)


    def test_data_qualified_max_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Qualified Max Cardinality -------
ex-kb:Assertion_1 {
    ex:hasPolynomialRoot rdf:type owl:DatatypeProperty ;
        rdfs:subPropertyOf sio:hasValue ;
        rdfs:label "has polynomial root" .

    ex-kb:QuadraticPolynomialRootRestriction rdf:type owl:Restriction ;
        owl:onProperty ex:hasPolynomialRoot ;
        owl:maxQualifiedCardinality "2"^^xsd:integer ;
        owl:onDataRange xsd:decimal .

    ex-kb:QuadraticPolynomialInstance rdf:type sio:Human ;
        rdfs:label "quadratic polynomial instance" ;
        ex:hasPolynomialRoot "1.23"^^xsd:decimal , "3.45"^^xsd:decimal , "5.67"^^xsd:decimal .

    #sio:InformationContentEntity rdf:type owl:Class ;
    #    rdfs:subClassOf sio:Object ;
    ##    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
    #    rdfs:label "information content entity" ;
    #    dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .
    #
    #sio:MathematicalEntity rdf:type owl:Class ;
    #    rdfs:subClassOf sio:InformationContentEntity ;
    #    rdfs:label "mathematical entity" ;
    #    dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .
    #
    #ex:hasPolynomialRoot rdf:type owl:DatatypeProperty ;
    #    rdfs:subPropertyOf sio:hasValue ;
    #    rdfs:label "has polynomial root" .
    #
    #ex-kb:QuadraticPolynomialRootRestriction rdf:type owl:Restriction ;
    #    owl:onProperty ex:hasPolynomialRoot ;
    #    owl:maxQualifiedCardinality "2"^^xsd:integer ;
    #    owl:onDataRange xsd:decimal .
    #
    #ex-kb:QuadraticPolynomialInstance rdf:type sio:ConceptualEntity ;
    #    rdfs:label "quadratic polynomial instance" ;
    #    ex:hasPolynomialRoot "1.23"^^xsd:decimal , "3.45"^^xsd:decimal , "5.67"^^xsd:decimal .
}

ex-kb:Assertion_2 {
    ex-kb:QuadraticPolynomialInstance rdf:type owl:Nothing .
}
# -------  Data Qualified Max Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Qualified Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        #objects = list(self.app.db.objects(KB.QuadraticPolynomialInstance, ONT.hasPolynomialRoot))
        #print(objects)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Qualified Max Cardinality Back Tracer')), self.app.db)


    def test_data_min_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Min Cardinality -------
ex:hasDiameterValue rdf:type owl:DatatypeProperty ;
    rdfs:subPropertyOf sio:hasValue ;
    rdfs:label "has diameter value" .

ex:ConicalCylinder rdf:type owl:Class ;
    rdfs:subClassOf
        [ rdf:type owl:Restriction ;
            owl:onProperty ex:hasDiameterValue ;
            owl:minCardinality "2"^^xsd:integer ] ;
    rdfs:label "conical cylinder" .

ex-kb:CoffeeContainer rdf:type ex:ConicalCylinder ;
    ex:hasDiameterValue "1"^^xsd:integer ;#, "2"^^xsd:integer  ;
    rdfs:label "coffee container" .

# come back to this
# -------  Data Min Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Min Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.CoffeeContainer, ONT.hasDiameterValue))
        self.assertEquals(len(objects), 2)

    def test_data_qualified_min_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Qualified Min Cardinality -------
ex:hasName rdf:type owl:DatatypeProperty ;
    rdfs:subPropertyOf sio:hasValue ;
    rdfs:label "has name" .

ex-kb:NameRestriction rdf:type owl:Restriction ;
    owl:onProperty ex:hasName ;
    owl:minQualifiedCardinality "2"^^xsd:integer ;
    owl:onDataRange xsd:string .

ex-kb:Jackson rdf:type sio:Human ;
    rdfs:label "Jackson" ;
    ex:hasName "Jackson"^^xsd:string .

#come back to this
# -------  Data Qualified Min Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Qualified Min Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.Jackson, ONT.hasName))
        self.assertEquals(len(objects), 2)

    def test_data_exact_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Exact Cardinality -------
ex-kb:Assertion_1 {
    ex:hasBirthYear rdf:type owl:DatatypeProperty ;
        rdfs:subPropertyOf sio:hasValue ;
        rdfs:label "has birth year" .

    ex:Person rdf:type owl:Class ;
        rdfs:label "person" ;
        rdfs:subClassOf sio:Human ;
        rdfs:subClassOf
            [ rdf:type owl:Restriction ;
                owl:onProperty ex:hasBirthYear ;
                owl:cardinality "1"^^xsd:integer ] . 

    ex-kb:Erik rdf:type ex:Person ;
        rdfs:label "Erik" ;
        ex:hasBirthYear "1988"^^xsd:integer , "1998"^^xsd:integer .
}

ex-kb:Assertion_2 {
    ex-kb:Erik rdf:type owl:Nothing .
}
# -------  Data Exact Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Exact Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Exact Cardinality Back Tracer')), self.app.db)

    def test_data_qualified_exact_cardinality_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Qualified Exact Cardinality -------
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex:uniqueUsername rdf:type owl:DatatypeProperty ;
        rdfs:subPropertyOf sio:hasValue ;
        rdfs:label "unique username" .

    ex-kb:UsernameRestriction rdf:type owl:Restriction ;
        owl:onProperty ex:uniqueUsername ;
        owl:qualifiedCardinality "1"^^xsd:integer ;
        owl:onDataRange xsd:string .

    ex-kb:Stephen rdf:type sio:Human ;
        rdfs:label "Steve" ;
        ex:uniqueUsername "SteveTheGamer"^^xsd:string , "ScubaSteve508"^^xsd:string .
}

ex-kb:Assertion_2 {
    ex-kb:Stephen rdf:type owl:Nothing .
}
# -------  Data Qualified Exact Cardinality ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Qualified Max Cardinality Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Qualified Max Cardinality Back Tracer')), self.app.db)
#        agent =  config.Config["inferencers"]["Data Qualified Min Cardinality"]
#        agent.process_graph(self.app.db)

    def test_object_complement_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Complement Of ------- 
ex-kb:Assertion_1 {
    ex:VitalStatus rdfs:subClassOf sio:Attribute ;
        rdfs:label "vital status" .

    ex:Dead rdf:type owl:Class ;
        rdfs:subClassOf ex:VitalStatus ;
        rdfs:label "dead" .

    ex:Alive rdf:type owl:Class ;
        rdfs:subClassOf ex:VitalStatus ;
        rdfs:label "alive" ;
        owl:complementOf ex:Dead .

    ex-kb:VitalStatusOfPat rdf:type ex:Alive , ex:Dead ;
        rdfs:label "Pat's Vital Status" ;
        sio:isAttributeOf ex-kb:Pat .

    ex-kb:Pat rdf:type sio:Human ;
        rdfs:label "Pat" .
}

ex-kb:Assertion_2 {
    ex-kb:VitalStatusOfPat rdf:type owl:Nothing .
}
# -------  Object Complement Of ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Complement Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Complement Of Back Tracer')), self.app.db)

    def test_object_property_complement_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Property Complement Of ------- 
ex-kb:Assertion_1 {
    sio:hasUnit rdf:type owl:ObjectProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has unit" ;
        owl:inverseOf sio:isUnitOf ;
        rdfs:range sio:UnitOfMeasurement ;
        rdfs:subPropertyOf sio:hasAttribute ;
        dct:description "has unit is a relation between a quantity and the unit it is a multiple of." .

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

    sio:MathematicalEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:InformationContentEntity ;
        rdfs:label "mathematical entity" ;
        dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .

    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
    #    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    ex-kb:Efficiency rdf:type sio:DimensionlessQuantity  ;
        sio:hasUnit [ rdf:type ex:Percentage ] ;
        rdfs:label "efficiency" .

    ex:Percentage rdfs:subClassOf sio:UnitOfMeasurement ;
        rdfs:label "percentage" .
}

ex-kb:Assertion_2 {
    ex-kb:Efficiency rdf:type owl:Nothing .
}
# -------  Object Property Complement Of ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Complement Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Property Complement Of Back Tracer')), self.app.db)

    def test_data_complement_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Complement Of ------- 
ex-kb:Assertion_1 {
    ex:nonTextValue rdf:type owl:DatatypeProperty ;
        rdfs:subClassOf sio:hasValue ;
        rdfs:label "non-text value" ;
        rdfs:range ex:NotAString .

    ex:NotAString rdf:type rdfs:Datatype ; 
        owl:datatypeComplementOf xsd:string .

    ex-kb:SamplePhrase rdf:type sio:TextualEntity ;
        rdfs:label "sample phrase" ;
        ex:nonTextValue "To be, or not to be?"^^xsd:string .
}

ex-kb:Assertion_2 {
    ex-kb:SamplePhrase rdf:type owl:Nothing .
}
# -------  Data Complement Of ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Complement Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Complement Of Back Tracer')), self.app.db)

    def test_data_property_complement_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Property Complement Of ------- 
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    ex:NumericalValue rdf:type owl:Class ;
        rdfs:label "numerical value" ;
        rdfs:subClassOf sio:ConceptualEntity ;
        rdfs:subClassOf
            [ rdf:type owl:Class ;
                owl:complementOf 
                    [ rdf:type owl:Restriction ;
                        owl:onProperty sio:hasValue ;
                        owl:someValuesFrom xsd:string ] 
            ] .

    ex-kb:Number rdf:type ex:NumericalValue ;
        sio:hasValue "Fifty"^^xsd:string .
}

ex-kb:Assertion_2 {
    ex-kb:Number rdf:type owl:Nothing .
}
# -------  Data Property Complement Of ------->
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Property Complement Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Property Complement Of Back Tracer')), self.app.db)

    def test_object_union_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Union Of ------- 
ex-kb:Assertion_1 {
    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
    #    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    sio:GeometricEntity rdf:type owl:Class ;
        rdfs:label "geometric entity" ;
        rdfs:subClassOf sio:InformationContentEntity ;
        dct:description "A geometric entity is an information content entity that pertains to the structure and topology of a space." .

    sio:Curve rdf:type owl:Class ;
        rdfs:label "curve" ;
        rdfs:subClassOf sio:GeometricEntity ;
        dct:description "A curve is a geometric entity that may be located in n-dimensional spatial region whose extension may be n-dimensional,  is composed of at least two fully connected points and does not intersect itself." .

    sio:Line rdf:type owl:Class ;
        rdfs:subClassOf sio:Curve ;
        rdfs:label "line" ;
        owl:equivalentClass 
            [   rdf:type owl:Class ;
                owl:unionOf ( sio:LineSegment sio:Ray sio:InfiniteLine ) ] ;
        dct:description "A line is curve that extends in a single dimension (e.g. straight line; exhibits no curvature), and is composed of at least two fully connected points." .
}

ex-kb:Assertion_2 {
    sio:LineSegment rdfs:subClassOf sio:Line .
    sio:Ray rdfs:subClassOf sio:Line .
    sio:InfiniteLine rdfs:subClassOf sio:Line .
}
# -------  Object Union Of -------> 
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Union Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Union Of Back Tracer')), self.app.db)

    def test_data_union_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Union Of ------- 
ex-kb:Assertion_1 {
    sio:hasValue rdf:type owl:DatatypeProperty ,
                                    owl:FunctionalProperty;
        rdfs:label "has value" ;
        dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

    sio:InformationContentEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:Object ;
    #    rdfs:subClassOf rdf:nodeID="arc0158b21" ;
        rdfs:label "information content entity" ;
        dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

    sio:MathematicalEntity rdf:type owl:Class ;
        rdfs:subClassOf sio:InformationContentEntity ;
        rdfs:label "mathematical entity" ;
        dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .

    sio:Number rdf:type owl:Class ;
        rdfs:label "number" ;
        rdfs:subClassOf sio:MathematicalEntity ;
        dct:description "A number is a mathematical object used to count, label, and measure." .

    sio:MeasurementValue rdf:type owl:Class ;
        rdfs:label "measurement value" ;
        rdfs:subClassOf sio:Number ;
        rdfs:subClassOf 
            [ rdf:type owl:Class ;
                owl:unionOf ( 
                    [ rdf:type owl:Restriction ; 
                        owl:onProperty sio:hasValue ;
                        owl:someValuesFrom xsd:dateTime ] 
                    [ rdf:type owl:Restriction ; 
                        owl:onProperty sio:hasValue ;
                        owl:someValuesFrom xsd:double ]
                    [ rdf:type owl:Restriction ; 
                        owl:onProperty sio:hasValue ;
                        owl:someValuesFrom xsd:float ]
                    [ rdf:type owl:Restriction ; 
                        owl:onProperty sio:hasValue ;
                        owl:someValuesFrom xsd:integer ]
                ) ] ;
        dct:description "A measurement value is a quantitative description that reflects the magnitude of some attribute." .

    ex-kb:DateTimeMeasurement rdf:type owl:Individual ;
        rdfs:label "date time measurement" ;
        sio:hasValue "10141990"^^xsd:dateTime .

    ex-kb:IntegerMeasurement rdf:type owl:Individual ;
        rdfs:label "integer measurement" ;
        sio:hasValue "12"^^xsd:integer .

    ex-kb:DoubleMeasurement rdf:type owl:Individual ;
        rdfs:label "double measurement" ;
        sio:hasValue "6.34"^^xsd:double .

    ex-kb:FloatMeasurement rdf:type owl:Individual ;
        rdfs:label "float measurement" ;
        sio:hasValue "3.14"^^xsd:float .
}

ex-kb:Assertion_2 {
    ex-kb:DateTimeMeasurement rdf:type sio:MeasurementValue .
    ex-kb:IntegerMeasurement rdf:type sio:MeasurementValue .
    ex-kb:DoubleMeasurement rdf:type sio:MeasurementValue .
    ex-kb:FloatMeasurement rdf:type sio:MeasurementValue .
}
# -------  Data Union Of -------> 
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Union Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Data Union Of Back Tracer')), self.app.db)

    def test_disjoint_union_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Disjoint Union ------- 
ex-kb:Assertion_1 {
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

    ex:Lobe rdf:type owl:Class ;
        rdfs:subClassOf sio:BiologicalEntity ;
        rdfs:label "lobe" ;
        dct:description "A lobe that is part the brain." ;
        owl:equivalentClass 
            [ rdf:type owl:Class ;
                owl:disjointUnionOf ( ex:FrontalLobe ex:ParietalLobe ex:TemporalLobe ex:OccipitalLobe ex:LimbicLobe ) ] .
}

ex-kb:Assertion_2 {
    ex:FrontalLobe rdfs:subClassOf ex:Lobe ;
        owl:disjointWith ex:ParietalLobe , ex:TemporalLobe , ex:OccipitalLobe , ex:LimbicLobe .

    ex:ParietalLobe rdfs:subClassOf ex:Lobe ;
        owl:disjointWith ex:FrontalLobe , ex:TemporalLobe , ex:OccipitalLobe , ex:LimbicLobe .

    ex:TemporalLobe rdfs:subClassOf ex:Lobe ;
        owl:disjointWith ex:FrontalLobe , ex:ParietalLobe , ex:OccipitalLobe , ex:LimbicLobe .

    ex:OccipitalLobe rdfs:subClassOf ex:Lobe ;
        owl:disjointWith ex:FrontalLobe , ex:ParietalLobe , ex:TemporalLobe , ex:LimbicLobe .

    ex:LimbicLobe rdfs:subClassOf ex:Lobe ;
        owl:disjointWith ex:FrontalLobe , ex:ParietalLobe , ex:TemporalLobe , ex:OccipitalLobe .
}
# -------  Disjoint Union -------> 
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Disjoint Union Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Disjoint Union Back Tracer')), self.app.db)

    def test_object_intersection_of_back_tracer(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Intersection Of ------- 
ex-kb:Assertion_1 {
    sio:Molecule rdf:type owl:Class ;
        rdfs:label "molecule" .

    sio:isTargetIn rdf:type owl:ObjectProperty ;
        rdfs:label "is target in" .

    sio:Target rdf:type owl:Class  ;
        owl:intersectionOf ( 
            sio:Molecule 
            [ rdf:type owl:Restriction ;
                owl:onProperty sio:isTargetIn ;
                owl:someValuesFrom sio:Process ] ) ;
        rdfs:label "target" .

    ex-kb:ProteinReceptor rdf:type sio:Molecule ;
        rdfs:label "protein receptor" ;
        sio:isTargetIn ex-kb:Therapy .

    ex-kb:Therapy rdf:type sio:Process ;
        rdfs:label "therapy" .

    # update following example. using it for testing for now
    ex-kb:Brian rdf:type ex:CanTalk , ex:Dog , ex:Friendly .

    ex:CanTalk rdf:type owl:Class .
    ex:Dog rdf:type owl:Class .
    ex:Friendly rdf:type owl:Class .

    ex:FriendlyTalkingDog rdf:type owl:Class ;
        owl:intersectionOf (ex:CanTalk ex:Dog ex:Friendly) .
}

ex-kb:Assertion_2 {
    ex-kb:ProteinReceptor rdf:type sio:Target .
}

ex-kb:Assertion_3 {
    ex-kb:Brian rdf:type ex:FriendlyTalkingDog .
}
# ------- Object Intersection Of -------> 
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Intersection Of Back Tracer"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Assertion_2, WHYIS.hypothesis, Literal('Object Intersection Of Back Tracer')), self.app.db)
        self.assertIn((KB.Assertion_3, WHYIS.hypothesis, Literal('Object Intersection Of Back Tracer')), self.app.db)

#    def test_data_intersection_of_back_tracer(self):
#        self.dry_run = False
#
#        np = nanopub.Nanopublication()
#        np.assertion.parse(data=prefixes+'''
## <------- Data Intersection Of ------- 
## Need to come back to this --> can't assign multiple datatypes to a literal. However, can assign a datatype and a restriction on that datatype.. but what would be constructed?
#ex:Zero rdf:type rdfs:Datatype ; 
#    rdfs:label "zero" ;
#    owl:intersectionOf ( xsd:nonNegativeInteger xsd:nonPositiveInteger ) .
#
#ex:TeenageValue rdf:type rdfs:Datatype ; 
#    rdfs:label "teenage value" ;
#    owl:intersectionOf ( 
#        xsd:integer 
#        [ rdf:type owl:Datatype ;
#            owl:onDatatype xsd:integer ;
#            owl:withRestrictions ( [ xsd:minInclusive "13"^^xsd:integer ] [ xsd:maxInclusive "19"^^xsd:integer ] ) 
#        ] ) .
## ------- Data Intersection Of -------> 
#''', format="trig")
#        self.app.nanopub_manager.publish(*[np])
#        agent =  config.Config["inferencers"]["Data Intersection Of"]
#        agent.process_graph(self.app.db)
#        self.assertIn((KB.ReplaceMe, RDF.type, OWL.Nothing), self.app.db)
