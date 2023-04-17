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

sio:Object rdf:type owl:Class ;
    rdfs:subClassOf sio:Entity ;
    rdfs:label "object" ;
    dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

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
# ------- Class Disjointness ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Class Disjointness"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.ImaginaryFriend, RDF.type, OWL.Nothing), self.app.db)

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
# ------- Object Property Transitivity ------->

''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Transitivity"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Fingernail, SIO.isPartOf, KB.Hand), self.app.db)

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
    dct:description "A process is an entity that is identifiable only through the unfolding of time, has temporal parts, and unless otherwise specified/predicted, cannot be identified from any instant of time in which it exists." ;
    rdfs:label "process" .

ex-kb:Workflow rdf:type sio:Process ;
    rdfs:label "workflow" ;
    sio:hasPart ex-kb:Step .

ex-kb:Step rdf:type sio:Process ;
    rdfs:label "step" .
# ------- Object Property Reflexivity  ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Reflexivity"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Workflow, SIO.hasPart, KB.Workflow), self.app.db)


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

sio:Entity rdf:type owl:Class ;
    rdfs:label "entity" ;
    dct:description "Every thing is an entity." .

sio:Object rdf:type owl:Class ;
    rdfs:subClassOf sio:Entity ;
    rdfs:label "object" ;
    dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

sio:InformationContentEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:Object ;
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
# ------- Object Property Irreflexivity  ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Irreflexivity"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Group, RDF.type, OWL.Nothing), self.app.db)

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

ex-kb:Tutor rdf:type sio:Human ;
    rdfs:label "tutor" .

ex-kb:Teacher rdf:type sio:Human ;
    rdfs:label "teacher" .

ex-kb:TeachingRole rdf:type sio:Role ;
    rdfs:label "teaching role" ;
    sio:isRoleOf ex-kb:Teacher , ex-kb:Tutor .
# ------- Functional Object Property ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Functional Object Property"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Teacher, OWL.sameAs,KB.Tutor), self.app.db)

    def test_object_property_domain(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Domain -------   
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
    dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

sio:MaterialEntity  rdf:type owl:Class ;
    rdfs:label "material entity" ;
    rdfs:subClassOf sio:Object ;
    dct:description "A material entity is a physical entity that is spatially extended, exists as a whole at any point in time and has mass." .

sio:ChemicalEntity  rdf:type owl:Class ;
    rdfs:label "chemical entity" ;
    rdfs:subClassOf sio:MaterialEntity ;
    dct:description "A chemical entity is a material entity that pertains to chemistry." .

sio:HeterogeneousSubstance  rdf:type owl:Class ;
    rdfs:label "heterogeneous substance" ;
    rdfs:subClassOf sio:MaterialEntity ;
    rdfs:subClassOf sio:ChemicalEntity ;
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
# ------- Object Property Domain ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Domain Assertion"]
        agent.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Property Domain Class Inclusion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object Property Domain Property Inclusion"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.Mother, RDF.type, SIO.Role), self.app.db)

    def test_data_property_domain(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Domain -------   

ex:hasAge rdf:type owl:DatatypeProperty ;
    rdfs:label "has age"^^xsd:String ;
    rdfs:subClassOf ex:hasAgeValue .

ex:hasAgeValue rdf:type owl:DatatypeProperty ;
    rdfs:label "has age value"^^xsd:String ;
    rdfs:domain sio:Age .

ex-kb:AgeOfJimmy ex:hasAgeValue "42"^^xsd:integer .

sio:Age rdf:type owl:Class ;
    rdfs:label "age"^^xsd:string ;
    rdfs:subClassOf sio:DimensionalQuantity .

#        ?p rdf:type owl:DatatypeProperty ;
#            rdfs:domain ?c1 .
#        ?c1 rdfs:subClassOf+ ?c2
#     ----> ?p rdfs:domain ?c2 .

#        ?p2 rdf:type owl:DatatypeProperty ;
#            rdfs:domain ?c .
#        ?p1 rdf:type owl:DatatypeProperty ;
#            rdfs:subPropertyOf ?p2
#       ----> ?p1 rdfs:domain ?c .

# ------- Data Property Domain ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Property Domain Assertion"]
        agent.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Data Property Domain Class Inclusion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Data Property Domain Property Inclusion"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.AgeOfJimmy, RDF.type, SIO.Age), self.app.db)
        self.assertIn((ONT.hasAgeValue, RDFS.domain, SIO.DimensionalQuantity), self.app.db)
        self.assertIn((ONT.hasAge, RDFS.domain, SIO.Age), self.app.db)


    def test_object_property_range(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Range -------
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
# ------- Object Property Range ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Property Range Assertion"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Property Range Class Inclusion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object Property Range Property Inclusion"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.Meter, RDF.type, SIO.UnitOfMeasurement), self.app.db)  # need more tests


    def test_data_property_range(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Range -------
ex:positiveInteger rdf:type owl:DatatypeProperty ;
    rdfs:label "positive integer"^^xsd:string ;
    rdfs:range xsd:nonNegativeInteger .

ex:evenPositiveInteger rdf:type owl:DatatypeProperty ;
    rdfs:label "even positive integer"^^xsd:string ;
    rdfs:subPropertyOf ex:positiveInteger .

xsd:nonNegativeInteger rdfs:subClassOf xsd:integer .

ex-kb:AgeOfHarry ex:positiveInteger ex-kb:HarrysAge ;
    rdfs:label "Age of Harry"^^xsd:string .


#?p rdf:type owl:DatatypeProperty ;
#            rdfs:range ?c1 .
#        ?c1 rdfs:subClassOf+ ?c2
# ------------> ?p rdfs:range ?c2 .


#?p2 rdf:type owl:DatatypeProperty ;
#            rdfs:range ?c .
#        ?p1 rdf:type owl:DatatypeProperty ;
#            rdfs:subPropertyOf ?p2
# ----------> ?p1 rdfs:range ?c .

# ------- Data Property Range ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Data Property Range Assertion"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Data Property Range Class Inclusion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Data Property Range Property Inclusion"]
        agent3.process_graph(self.app.db)
        self.assertIn((ONT.positiveInteger, RDFS.range, XSD.integer), self.app.db) # <-- why isn't this working!? come back to this <--- works in blazegraph
        self.assertIn((KB.HarrysAge, RDF.type, XSD.nonNegativeInteger), self.app.db)
        self.assertIn((ONT.evenPositiveInteger, RDFS.range, XSD.nonNegativeInteger), self.app.db) # <-- why isn't this working!? come back to this <--- works in blazegraph

    def test_inverse_functional_object_property(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Inverse Functional Object Property -------
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
# ------- Inverse Functional Object Property ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Inverse Functional Object Property"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Water, OWL.sameAs, KB.HyrdogenDioxide), self.app.db)

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
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Functional Data Property"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.HeightOfTom, RDF.type, OWL.Nothing), self.app.db)

    def test_object_property_disjointness(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Disjointness -------
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
# ------- Object Property Disjointness ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Disjointness"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Susan, RDF.type, OWL.Nothing), self.app.db)


    def test_data_property_disjointness(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Disjointness -------
#         ?x ?p1 ?y .
#        ?x ?p2 ?y .
#        ?p1 rdf:type owl:DatatypeProperty .
#        ?p2 rdf:type owl:DatatypeProperty .
#        {?p1 owl:propertyDisjointWith ?p2 .}
#            UNION
#        {?p2 owl:propertyDisjointWith ?p1 .}
# ----> ?x rdf:type owl:Nothing .

ex-kb:Susan rdf:type sio:Human ;
    rdfs:label "Susan" ;
    ex:startTime "10"^^xsd:integer ;
    ex:endTime "10"^^xsd:integer .

ex:startTime rdf:type owl:DatatypeProperty ;
    rdfs:label "start time"^^xsd:string ;
    owl:propertyDisjointWith ex:endTime .

ex:endTime rdf:type owl:DatatypeProperty ;
    rdfs:label "end time"^^xsd:string .
    

# ------- Data Property Disjointness ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Property Disjointness"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Susan, RDF.type, OWL.Nothing), self.app.db)



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
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Symmetry"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Samantha, SIO.isRelatedTo, KB.Peter), self.app.db)

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
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Asymmetry"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Face, RDF.type, OWL.Nothing), self.app.db)

    def test_class_inclusion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Inclusion ------- 
sio:Entity rdf:type owl:Class ;
    rdfs:label "entity" ;
    dct:description "Every thing is an entity." .

sio:Object rdf:type owl:Class ;
    rdfs:subClassOf sio:Entity ;
    rdfs:label "object" ;
    dct:description "An object is an entity that is wholly identifiable at any instant of time during which it exists." .

sio:MaterialEntity  rdf:type owl:Class ;
    rdfs:label "material entity" ;
    rdfs:subClassOf sio:Object ;
    dct:description "A material entity is a physical entity that is spatially extended, exists as a whole at any point in time and has mass." .
# ------- Class Inclusion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Class Inclusion"]
        agent.process_graph(self.app.db)
        self.assertIn((SIO.MaterialEntity, RDFS.subClassOf, SIO.Entity), self.app.db)

    def test_object_property_inclusion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Inclusion -------
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
    dct:description "A quantity is an informational entity that gives the magnitude of a property." .

sio:MeasurementValue rdf:type owl:Class ;
    rdfs:label "measurement value" ;
    rdfs:subClassOf sio:Number ;
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
    rdfs:label "information content entity" ;
    dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

ex-kb:Samantha sio:hasProperty ex-kb:AgeOfSamantha .

ex-kb:AgeOfSamantha rdf:type sio:Age ;
    rdfs:label "Samantha's age" .
# ------- Object Property Inclusion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Property Inclusion Assertion"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Property Inclusion Subsumption"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.Samantha, SIO.hasAttribute, KB.AgeOfSamantha), self.app.db)

    def test_data_property_inclusion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Inclusion -------

#        ?resource ?p ?o .
#        ?p rdf:type owl:DatatypeProperty ;
#            rdfs:subPropertyOf+ ?superProperty .
#   ----> ?resource ?superProperty ?o .

#        ?p1 rdf:type owl:DatatypeProperty .
#        ?p2 rdf:type owl:DatatypeProperty .
#        ?p3 rdf:type owl:DatatypeProperty .
#        ?p1 rdfs:subPropertyOf ?p2 .
#        ?p2 rdfs:subPropertyOf+ ?p3 .
#    ----> ?p1 rdfs:subPropertyOf ?p3 .


sio:hasValue rdf:type owl:DatatypeProperty ,
                                owl:FunctionalProperty;
    rdfs:label "has value" ;
    dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

ex-kb:AgeOfSamantha rdf:type sio:Age ;
    rdfs:label "Samantha's age" .


ex:hasTrueValue rdf:type owl:DatatypeProperty ;
    rdfs:label "has true value" ;
    rdfs:subPropertyOf ex:hasExactValue .

ex:hasExactValue rdf:type owl:DatatypeProperty ;
    rdfs:label "has exact value" ;
    rdfs:subPropertyOf sio:hasValue .

ex-kb:AgeOfSamantha ex:hasExactValue "25.82"^^xsd:decimal .
# ------- Data Property Inclusion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Data Property Inclusion Assertion"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Data Property Inclusion Subsumption"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.AgeOfSamantha, SIO.hasValue, Literal('25.82', datatype=XSD.decimal)), self.app.db) #<-- why doesn't this work?
        self.assertIn((ONT.hasTrueValue, RDFS.subPropertyOf, SIO.hasValue), self.app.db) #<-- why doesn't this work?

    def test_property_chain_inclusion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Chain Inclusion -------
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
# ------- Object Property Chain Inclusion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Chain Inclusion"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Rug, SIO.overlapsWith, KB.Floor), self.app.db)

    def test_class_equivalence (self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Class Equivalence -------
#        ?x rdf:type ?c1 .
#        {?c1 owl:equivalentClass ?c2 .}
#            UNION
#        {?c2 owl:equivalentClass ?c1 .}
#        ---->?x rdf:type ?c2 .
#        
#        
#        {?c1 owl:equivalentClass ?c2 .}
#            UNION
#        {?c2 owl:equivalentClass ?c1 .}
#        ----> ?c1 rdfs:subClassOf ?c2 . ?c2 rdfs:subClassOf ?c1 .
#        
#        
#        ?c1 rdfs:subClassOf ?c2 .
#        ?c2 rdfs:subClassOf ?c1 .
#        ---->?c1 owl:equivalentClass ?c2 .


ex:Fake rdf:type owl:Class ;
    owl:equivalentClass sio:Fictional ;
    rdfs:label "fake" .

sio:Real rdfs:subClassOf ex:Truth .
ex:Truth rdfs:subClassOf sio:Real .

ex-kb:Hubert rdf:type ex:Fake ;
    rdfs:label "Hubert" .
# ------- Class Equivalence ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Class Equivalence Substitution"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Class Equivalence Expansion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Class Equivalence Contraction"]
        agent3.process_graph(self.app.db)
        #self.assertIn((KB.Hubert, RDF.type, SIO.Fictional), self.app.db) # why doesn't this work?
        #self.assertIn((ONT.Fake, RDFS.subClassOf, SIO.Fictional), self.app.db) # <-- didn't show up
        #self.assertIn((SIO.Fictional, RDFS.subClassOf, ONT.Fake), self.app.db) # <-- also didn't show up
        self.assertIn((SIO.Real, OWL.equivalentClass, ONT.Truth), self.app.db) # also doesn't show up   # note all of these show up in blazegraph

    def test_object_property_equivalence(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Equivalence -------
sio:isRelatedTo rdf:type owl:ObjectProperty ,
                                owl:SymmetricProperty ;
    rdfs:label "is related to" ;
    dct:description "A is related to B iff there is some relation between A and B." .

ex:hasRelationshipWith rdf:type owl:ObjectProperty ;
    rdfs:label "has relationship"^^xsd:string ;
    owl:equivalentProperty sio:isRelatedTo .

ex-kb:Hillary ex:hasRelationshipWith ex-kb:Bill .
# ------- Object Property Equivalence ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Property Equivalence Substitution"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Property Equivalence Expansion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object Property Equivalence Contraction"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.Hillary, SIO.isRelatedTo,KB.Bill), self.app.db)

    def test_data_property_equivalence(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Data Property Equivalence -------
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
# ------- Data Property Equivalence ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Data Property Equivalence Substitution"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Data Property Equivalence Expansion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Data Property Equivalence Contraction"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.AgeOfSamantha, ONT.hasValue,Literal('25.82', datatype=XSD.decimal)), self.app.db)

    def test_individual_inclusion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Individual Inclusion -------
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
# -------  Individual Inclusion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Individual Inclusion"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Reliable, RDF.type, SIO.Attribute), self.app.db)
        self.assertIn((KB.Reliable, RDF.type, SIO.Entity), self.app.db)

    def test_object_property_inversion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Property Inversion -------
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
# ------- Object Property Inversion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Inversion"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Finger, SIO.hasPart, KB.Fingernail), self.app.db)

    def test_same_individual(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Same Individual -------
ex-kb:Peter rdf:type sio:Human ;
    rdfs:label "Peter" ;
    sio:isRelatedTo ex-kb:Samantha .

ex-kb:Samantha rdf:type sio:Human ;
    rdfs:label "Samantha" .

ex-kb:Peter owl:sameAs ex-kb:Pete .
# -------  Same Individual ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        #agent =  config.Config["inferencers"]["Same Subject"]  # currently commented out in code, so commenting out for now
        #agent.process_graph(self.app.db)
        #self.assertIn((KB.Pete, RDF.type, SIO.Human), self.app.db)
        #self.assertIn((KB.Pete, RDFS.label, Literal('Peter')), self.app.db)
        #self.assertIn((KB.Pete, SIO.isRelatedTo, KB.Samantha), self.app.db)

    def test_different_individuals(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Different Individuals ------- 
ex-kb:Sam owl:differentFrom ex-kb:Samantha .
ex-kb:Sam owl:sameAs ex-kb:Samantha .
# -------  Different Individuals ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Different Individuals"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Sam, RDF.type, OWL.Nothing), self.app.db)


#    def test_positive_object_property_assertion(self):
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
#''', format="turtle")
#        self.app.nanopub_manager.publish(*[np])
#        agent =  config.Config["inferencers"]["Positive Object Property Assertion"]
#        agent.process_graph(self.app.db)
#        self.assertIn((KB.ReplaceMe, RDF.type, OWL.Nothing), self.app.db)
#
#    def test_positive_data_property_assertion(self):
#        self.dry_run = False
#
#        np = nanopub.Nanopublication()
#        np.assertion.parse(data=prefixes+'''
## <------- Positive Data Property Assertion ------- 
## Need to come back to this
# -------  Positive Data Property Assertion -------> 
#''', format="turtle")
#        self.app.nanopub_manager.publish(*[np])
#        agent =  config.Config["inferencers"]["Positive Data Property Assertion"]
#        agent.process_graph(self.app.db)
#        self.assertIn((KB.ReplaceMe, RDF.type, OWL.Nothing), self.app.db)

    def test_negative_object_property_assertion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Negative Object Property Assertion -------
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
# -------  Negative Object Property Assertion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Negative Object Property Assertion"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.AgeOfSamantha, RDF.type, OWL.Nothing), self.app.db)

    def test_negative_data_property_assertion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Negative DataPropertyAssertion -------
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
# -------  Negative DataProperty Assertion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Negative Data Property Assertion"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.AgeOfPeter, RDF.type, OWL.Nothing), self.app.db)

    def test_keys(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Keys -------
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
# ------- Keys ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Single Key"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Multiple Keys"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.John, OWL.sameAs, KB.Jack), self.app.db)

    def test_object_some_values_from(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Some Values From -------
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
# -------  Object Some Values From ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Some Values From Assertion"]
        agent1.process_graph(self.app.db)
        #agent2 =  config.Config["inferencers"]["Object Some Values From Class Inclusion"]
        #agent2.process_graph(self.app.db)
        #agent3 =  config.Config["inferencers"]["Object Some Values From Property Inclusion"]
        #agent3.process_graph(self.app.db)   # currently commented out in square code, so commenting out here for now
        self.assertIn((KB.MolecularCollection, RDF.type, SIO.CollectionOf3dMolecularStructureModels), self.app.db)

    def test_data_some_values_from(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Some Values From -------
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
# -------  Data Some Values From ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Some Values From"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Question, RDF.type, OWL.Nothing), self.app.db)

    def test_object_has_self(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Has Self -------
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
# -------  Object Has Self ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Has Self Reflexivity"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Has Self Assertion"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.Blue, SIO.hasAttribute, KB.Blue), self.app.db)

    def test_object_has_value(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Has Value -------
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
# -------  Object Has Value ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Has Value One"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Has Value Two"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.Car, SIO.hasPart, KB.Wheel), self.app.db)

    def test_data_has_value(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Has Value -------
sio:hasValue rdf:type owl:DatatypeProperty ,
                                owl:FunctionalProperty;
    rdfs:label "has value" ;
    dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .

ex:hasAge rdf:type owl:DatatypeProperty ;
    rdfs:label "has age" ;
    rdfs:subPropertyOf sio:hasValue .
    
ex:Unliked rdf:type owl:Class ;
    owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ex:hasAge ;
            owl:hasValue "23"^^xsd:integer ] .

ex-kb:Tom ex:hasAge "23"^^xsd:integer .
# -------  Data Has Value ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Has Value"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Tom, RDF.type, ONT.Unliked), self.app.db)

    def test_all_disjoint_classes(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  All Disjoint Classes-------
sio:Entity rdf:type owl:Class ;
    rdfs:label "entity" ;
    dct:description "Every thing is an entity." .

sio:Process rdf:type owl:Class ;
    rdfs:subClassOf sio:Entity ;
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

[ rdf:type owl:AllDisjointClasses ;
    owl:members ( sio:Process sio:Attribute sio:Object ) ] .
# -------  All Disjoint Classes ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Disjoint Classes"]
        agent.process_graph(self.app.db)
        self.assertIn((SIO.Process,OWL.disjointWith,SIO.Attribute), self.app.db)
        self.assertIn((SIO.Process,OWL.disjointWith,SIO.Object), self.app.db)
        self.assertIn((SIO.Attribute,OWL.disjointWith,SIO.Process), self.app.db)
        self.assertIn((SIO.Attribute,OWL.disjointWith,SIO.Object), self.app.db)
        self.assertIn((SIO.Object,OWL.disjointWith,SIO.Process), self.app.db)
        self.assertIn((SIO.Object,OWL.disjointWith,SIO.Attribute), self.app.db)

    def test_all_disjoint_properties(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  All Disjoint Properties-------
ex-kb:DisjointPropertiesRestriction rdf:type owl:AllDisjointProperties ;
    owl:members ( ex:hasMother ex:hasFather ex:hasSibling ) .

ex:hasMother rdf:type owl:ObjectProperty ;
    rdfs:label "has mother" .

ex:hasFather rdf:type owl:ObjectProperty ;
    rdfs:label "has father" .

ex:hasSibling rdf:type owl:ObjectProperty ;
    rdfs:label "has sibling" .
# -------  All Disjoint Properties ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Disjoint Properties"]
        agent.process_graph(self.app.db)
        self.assertIn((ONT.hasMother, OWL.propertyDisjointWith, ONT.hasFather), self.app.db)
        self.assertIn((ONT.hasMother, OWL.propertyDisjointWith, ONT.hasSibling), self.app.db)
        self.assertIn((ONT.hasFather, OWL.propertyDisjointWith, ONT.hasMother), self.app.db)
        self.assertIn((ONT.hasFather, OWL.propertyDisjointWith, ONT.hasSibling), self.app.db)
        self.assertIn((ONT.hasSibling, OWL.propertyDisjointWith, ONT.hasMother), self.app.db)
        self.assertIn((ONT.hasSibling, OWL.propertyDisjointWith, ONT.hasFather), self.app.db)

    def test_all_different_individuals(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  All Different Individuals-------
ex-kb:DistinctTypesRestriction rdf:type owl:AllDifferent ;
    owl:distinctMembers
        ( ex-kb:Integer
        ex-kb:String 
        ex-kb:Boolean
        ex-kb:Double 
        ex-kb:Float 
        ex-kb:Tuple 
        ) .
# -------  All Different Individuals------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["All Different Individuals"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Integer, OWL.differentFrom, KB.String), self.app.db)
        self.assertIn((KB.Integer, OWL.differentFrom, KB.Boolean), self.app.db)
        self.assertIn((KB.Integer, OWL.differentFrom, KB.Double), self.app.db)
        self.assertIn((KB.Integer, OWL.differentFrom, KB.Float), self.app.db)
        self.assertIn((KB.Integer, OWL.differentFrom, KB.Tuple), self.app.db)
        self.assertIn((KB.String, OWL.differentFrom, KB.Integer), self.app.db)
        self.assertIn((KB.String, OWL.differentFrom, KB.Boolean), self.app.db)
        self.assertIn((KB.String, OWL.differentFrom, KB.Double), self.app.db)
        self.assertIn((KB.String, OWL.differentFrom, KB.Float), self.app.db)
        self.assertIn((KB.String, OWL.differentFrom, KB.Tuple), self.app.db)
        self.assertIn((KB.Boolean, OWL.differentFrom, KB.Integer), self.app.db)
        self.assertIn((KB.Boolean, OWL.differentFrom, KB.String), self.app.db)
        self.assertIn((KB.Boolean, OWL.differentFrom, KB.Double), self.app.db)
        self.assertIn((KB.Boolean, OWL.differentFrom, KB.Float), self.app.db)
        self.assertIn((KB.Boolean, OWL.differentFrom, KB.Tuple), self.app.db)
        self.assertIn((KB.Double, OWL.differentFrom, KB.Integer), self.app.db)
        self.assertIn((KB.Double, OWL.differentFrom, KB.String), self.app.db)
        self.assertIn((KB.Double, OWL.differentFrom, KB.Boolean), self.app.db)
        self.assertIn((KB.Double, OWL.differentFrom, KB.Float), self.app.db)
        self.assertIn((KB.Double, OWL.differentFrom, KB.Tuple), self.app.db)
        self.assertIn((KB.Float, OWL.differentFrom, KB.Integer), self.app.db)
        self.assertIn((KB.Float, OWL.differentFrom, KB.String), self.app.db)
        self.assertIn((KB.Float, OWL.differentFrom, KB.Boolean), self.app.db)
        self.assertIn((KB.Float, OWL.differentFrom, KB.Double), self.app.db)
        self.assertIn((KB.Float, OWL.differentFrom, KB.Tuple), self.app.db)
        self.assertIn((KB.Tuple, OWL.differentFrom, KB.Integer), self.app.db)
        self.assertIn((KB.Tuple, OWL.differentFrom, KB.String), self.app.db)
        self.assertIn((KB.Tuple, OWL.differentFrom, KB.Boolean), self.app.db)
        self.assertIn((KB.Tuple, OWL.differentFrom, KB.Double), self.app.db)
        self.assertIn((KB.Tuple, OWL.differentFrom, KB.Float), self.app.db)

    def test_object_one_of_assertion(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object One Of Assertion -------
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
# -------  Object One Of Assertion ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        #agent =  config.Config["inferencers"]["All Different Individuals"]
        #agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object One Of Assertion"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Integer, RDF.type, ONT.Type), self.app.db)
        self.assertIn((KB.String, RDF.type, ONT.Type), self.app.db)
        self.assertIn((KB.Boolean, RDF.type, ONT.Type), self.app.db)
        self.assertIn((KB.Double, RDF.type, ONT.Type), self.app.db)
        self.assertIn((KB.Float, RDF.type, ONT.Type), self.app.db)

    def test_object_one_of_inconsistency(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object One Of Inconsistency-------
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
# -------  Object One Of Inconsistency ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        #agent =  config.Config["inferencers"]["All Different Individuals"]
        #agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object One Of Inconsistency"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Tuple, RDF.type, OWL.Nothing), self.app.db)

    def test_data_one_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data One Of -------
# Need to come back to this
ex:hasTeenAge rdf:type owl:DatatypeProperty ;
    rdfs:label "has age" ;
    rdfs:range [ rdf:type owl:DataRange ;
        owl:oneOf ("13"^^xsd:integer "14"^^xsd:integer "15"^^xsd:integer "16"^^xsd:integer "17"^^xsd:integer "18"^^xsd:integer "19"^^xsd:integer )].

ex-kb:Sarah ex:hasTeenAge "12"^^xsd:integer .
# Note that we need to update range rule to account for data ranges
# -------  Data One Of ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data One Of"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Sarah, RDF.type, OWL.Nothing), self.app.db)

    def test_datatype_restriction(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Datatype Restriction -------
# Need to come back to this
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
    rdfs:label "probability value" .

ex-kb:EffortExerted rdf:type sio:ProbabilityValue ;
    rdfs:label "effort exerted" ;
    sio:hasValue "1.1"^^xsd:double .

#_:x rdf:type rdfs:Datatype.
#_:x owl:onDatatype DN.
#_:x owl:withRestrictions (_:x1 ... _:xn).
#_:xj fj vj.      j=1…n
# ------- Datatype Restriction ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Datatype Restriction"]
        agent.process_graph(self.app.db)
        
        agent2 =  config.Config["inferencers"]["Datatype Data Range Restriction"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.EffortExerted, RDF.type, OWL.Nothing), self.app.db)

    def test_object_all_values_from(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object All Values From -------
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
# -------  Object All Values From ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object All Values From Assertion"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object All Values From Class Inclusion"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object All Values From Property Inclusion"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.NamespaceID, RDF.type, SIO.Identifier), self.app.db)

    def test_data_all_values_from(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data All Values From -------
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
# -------  Data All Values From ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Data All Values From Assertion"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Data All Values From Inconsistency"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.Ten, RDF.type, OWL.Nothing), self.app.db)

    def test_object_max_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Max Cardinality -------
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
# -------  Object Max Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        #agent =  config.Config["inferencers"]["All Different Individuals"]
        #agent.process_graph(self.app.db)
        agent1 =  config.Config["inferencers"]["Object Max Cardinality One"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Max Cardinality Two"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object Max Cardinality Three"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.SevenDeadlySins, RDF.type, OWL.Nothing), self.app.db)

    def test_object_qualified_max_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Max Qualified Cardinality -------
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
    dct:description "A line segment is a line and a part of a curve that is (inclusively) bounded by two terminal points." ;
    rdfs:label "line segment" .

sio:DirectedLineSegment rdf:type owl:Class ;
    rdfs:subClassOf sio:LineSegment ;
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
# -------  Object Max Qualified Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Max Qualified Cardinality One"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Max Qualified Cardinality Two"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object Max Qualified Cardinality Three"]
        agent3.process_graph(self.app.db)
        agent4 =  config.Config["inferencers"]["Object Max Qualified Cardinality Four"]
        agent4.process_graph(self.app.db)
        agent5 =  config.Config["inferencers"]["Object Max Qualified Cardinality Five"]
        agent5.process_graph(self.app.db)
        self.assertIn((KB.TripleArrowLineSegment, RDF.type, OWL.Nothing), self.app.db)

    def test_object_min_cardinality(self):
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
# -------  Object Min Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        #agent =  config.Config["inferencers"]["All Different Individuals"]
        #agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Object Min Cardinality"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.StudyGroupInstance, SIO.hasMember))
        self.assertEquals(len(objects), 2)


    def test_object_qualified_min_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Min Qualified Cardinality -------
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
    dct:description "A line segment is a line and a part of a curve that is (inclusively) bounded by two terminal points." ;
    rdfs:label "line segment" .

ex-kb:PolylineSegment rdf:type sio:Polyline ;
    rdfs:label "polyline segment " ;
    sio:hasComponentPart ex-kb:LineSegmentInstance .

ex-kb:LineSegmentInstance rdf:type sio:LineSegment ;
    rdfs:label "line segment instance" .
# -------  Object Min Qualified Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Min Qualified Cardinality"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.PolylineSegment, SIO.hasComponentPart))
        self.assertEquals(len(objects), 2)

    def test_object_exact_cardinality(self):
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
# -------  Object Exact Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Exact Cardinality"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Stooges, RDF.type, OWL.Nothing), self.app.db)

    def test_object_qualified_exact_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Exact Qualified Cardinality -------
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
# -------  Object Exact Qualified Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Exact Qualified Cardinality"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.TripleVertexPolyEdge, RDF.type, OWL.Nothing), self.app.db)

    def test_data_max_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Max Cardinality -------
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
# -------  Data Max Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Max Cardinality"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Katie, RDF.type, OWL.Nothing), self.app.db)


    def test_data_qualified_max_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Max Qualified Cardinality -------
sio:InformationContentEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:Object ;
    rdfs:label "information content entity" ;
    dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

sio:MathematicalEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:InformationContentEntity ;
    rdfs:label "mathematical entity" ;
    dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .

ex:hasPolynomialRoot rdf:type owl:DatatypeProperty ;
    rdfs:subPropertyOf sio:hasValue ;
    rdfs:label "has polynomial root" .

ex-kb:QuadraticPolynomialRootRestriction rdf:type owl:Restriction ;
    owl:onProperty ex:hasPolynomialRoot ;
    owl:maxQualifiedCardinality "2"^^xsd:integer ;
    owl:onDataRange xsd:decimal .

ex-kb:QuadraticPolynomialInstance rdf:type sio:MathematicalEntity ;
    rdfs:label "quadratic polynomial instance" ;
    ex:hasPolynomialRoot "1.23"^^xsd:decimal , "3.45"^^xsd:decimal , "5.67"^^xsd:decimal .
# -------  Data Max Qualified Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Max Qualified Cardinality"]
        agent.process_graph(self.app.db)
        #objects = list(self.app.db.objects(KB.QuadraticPolynomialInstance, ONT.hasPolynomialRoot))
        #print(objects)
        self.assertIn((KB.QuadraticPolynomialInstance, RDF.type, OWL.Nothing), self.app.db)


    def test_data_min_cardinality(self):
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
# -------  Data Min Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Min Cardinality"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.CoffeeContainer, ONT.hasDiameterValue))
        self.assertEquals(len(objects), 2)

    def test_data_qualified_min_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Min Qualified Cardinality -------
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
# -------  Data Min Qualified Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Min Qualified Cardinality"]
        agent.process_graph(self.app.db)
        objects = list(self.app.db.objects(KB.Jackson, ONT.hasName))
        self.assertEquals(len(objects), 2)

    def test_data_exact_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Exact Cardinality -------
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
# -------  Data Exact Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Exact Cardinality"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Erik, RDF.type, OWL.Nothing), self.app.db)

    def test_data_qualified_exact_cardinality(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Exact Qualified Cardinality -------
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
# -------  Data Exact Qualified Cardinality ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Exact Qualified Cardinality"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Stephen, RDF.type, OWL.Nothing), self.app.db)

    def test_object_complement_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Complement Of ------- 
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
# -------  Object Complement Of ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Complement Of"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.VitalStatusOfPat, RDF.type, OWL.Nothing), self.app.db)

    def test_object_property_complement_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Property Complement Of ------- 
# Need to come back to this
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
    dct:description "A quantity is an informational entity that gives the magnitude of a property." .

sio:MeasurementValue rdf:type owl:Class ;
    rdfs:label "measurement value" ;
    rdfs:subClassOf sio:Number ;
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
    rdfs:label "information content entity" ;
    dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .

ex-kb:Efficiency rdf:type sio:DimensionlessQuantity  ;
    sio:hasUnit [ rdf:type ex:Percentage ] ;
    rdfs:label "efficiency" .

ex:Percentage rdfs:subClassOf sio:UnitOfMeasurement ;
    rdfs:label "percentage" .
# -------  Object Property Complement Of ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Object Property Complement Of"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Efficiency, RDF.type, OWL.Nothing), self.app.db)

    def test_data_complement_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Complement Of ------- 
ex:nonTextValue rdf:type owl:DatatypeProperty ;
    rdfs:subClassOf sio:hasValue ;
    rdfs:label "non-text value" ;
    rdfs:range ex:NotAString .

ex:NotAString rdf:type rdfs:Datatype ; 
    owl:datatypeComplementOf xsd:string .

ex-kb:SamplePhrase rdf:type sio:TextualEntity ;
    rdfs:label "sample phrase" ;
    ex:nonTextValue "To be, or not to be?"^^xsd:string .
# -------  Data Complement Of ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Complement Of"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.SamplePhrase, RDF.type, OWL.Nothing), self.app.db)

    def test_data_property_complement_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Property Complement Of ------- 
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
# -------  Data Property Complement Of ------->
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Data Property Complement Of"]
        agent.process_graph(self.app.db)
        self.assertIn((KB.Number, RDF.type, OWL.Nothing), self.app.db)

    def test_object_union_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Object Union Of ------- 
sio:InformationContentEntity rdf:type owl:Class ;
    rdfs:subClassOf sio:Object ;
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
# -------  Object Union Of -------> 
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Union Of One"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Union Of Two"]
        agent2.process_graph(self.app.db)
        self.assertIn((SIO.LineSegment, RDFS.subClassOf, SIO.Line), self.app.db)
        self.assertIn((SIO.Ray, RDFS.subClassOf, SIO.Line), self.app.db)
        self.assertIn((SIO.InfiniteLine, RDFS.subClassOf, SIO.Line), self.app.db)# Should come back to these.. shouldn't these be equivalent class links rather than subclassof

    def test_data_union_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Data Union Of ------- 


#        ?c rdf:type rdfs:Datatype ;
#            (owl:equivalentClass*|rdfs:subClassOf*)/owl:unionOf ?x .
#        ?x rdf:rest*/rdf:first ?ci .
#        ?y rdf:type ?ci.
# -----> ?y rdf:type ?c .

ex:StringInteger rdf:type rdfs:Datatype ;
    owl:unionOf ( xsd:string xsd:integer ) .

ex-kb:StringIntegerInstance rdf:type xsd:string , xsd:integer .


#        ?c rdf:type rdfs:Datatype ;
#            (owl:equivalentClass*|rdfs:subClassOf*)/owl:unionOf ?x .
#        ?x rdf:rest*/rdf:first ?ci .
# -----> ?ci rdfs:subClassOf ?c .


#sio:hasValue rdf:type owl:DatatypeProperty ,
#                                owl:FunctionalProperty;
#    rdfs:label "has value" ;
#    dct:description "A relation between a informational entity and its actual value (numeric, date, text, etc)." .
#
#sio:InformationContentEntity rdf:type owl:Class ;
#    rdfs:subClassOf sio:Object ;
#    rdfs:label "information content entity" ;
#    dct:description "An information content entity is an object that requires some background knowledge or procedure to correctly interpret." .
#
#sio:MathematicalEntity rdf:type owl:Class ;
#    rdfs:subClassOf sio:InformationContentEntity ;
#    rdfs:label "mathematical entity" ;
#    dct:description "A mathematical entity is an information content entity that are components of a mathematical system or can be defined in mathematical terms." .
#
#sio:Number rdf:type owl:Class ;
#    rdfs:label "number" ;
#    rdfs:subClassOf sio:MathematicalEntity ;
#    dct:description "A number is a mathematical object used to count, label, and measure." .
#
#sio:MeasurementValue rdf:type owl:Class ;
#    rdfs:label "measurement value" ;
#    rdfs:subClassOf sio:Number ;
#    rdfs:subClassOf 
#        [ rdf:type owl:Class ;
#            owl:unionOf ( 
#                [ rdf:type owl:Restriction ; 
#                    owl:onProperty sio:hasValue ;
#                    owl:someValuesFrom xsd:dateTime ] 
#                [ rdf:type owl:Restriction ; 
#                    owl:onProperty sio:hasValue ;
#                    owl:someValuesFrom xsd:double ]
#                [ rdf:type owl:Restriction ; 
#                    owl:onProperty sio:hasValue ;
#                    owl:someValuesFrom xsd:float ]
#                [ rdf:type owl:Restriction ; 
#                    owl:onProperty sio:hasValue ;
#                    owl:someValuesFrom xsd:integer ]
#            ) ] ;
#    dct:description "A measurement value is a quantitative description that reflects the magnitude of some attribute." .
#
#ex-kb:DateTimeMeasurement rdf:type owl:Individual ;
#    rdfs:label "date time measurement" ;
#    sio:hasValue "1990-10-14T21:32:52"^^xsd:dateTime .
#
#ex-kb:IntegerMeasurement rdf:type owl:Individual ;
#    rdfs:label "integer measurement" ;
#    sio:hasValue "12"^^xsd:integer .
#
#ex-kb:DoubleMeasurement rdf:type owl:Individual ;
#    rdfs:label "double measurement" ;
#    sio:hasValue "6.34"^^xsd:double .
#
#ex-kb:FloatMeasurement rdf:type owl:Individual ;
#    rdfs:label "float measurement" ;
#    sio:hasValue "3.14"^^xsd:float .
# -------  Data Union Of -------> 
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Data Union Of One"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Data Union Of Two"]
        agent2.process_graph(self.app.db)
        self.assertIn((KB.StringIntegerInstance, RDF.type, ONT.StringInteger), self.app.db)
        self.assertIn((XSD.string, RDFS.subClassOf, ONT.StringInteger), self.app.db)
        self.assertIn((XSD.integer, RDFS.subClassOf, ONT.StringInteger), self.app.db)
#        self.assertIn((KB.DateTimeMeasurement, RDF.type, SIO.MeasurementValue), self.app.db)
#        self.assertIn((KB.IntegerMeasurement, RDF.type, SIO.MeasurementValue), self.app.db)
#        self.assertIn((KB.DoubleMeasurement, RDF.type, SIO.MeasurementValue), self.app.db)
#        self.assertIn((KB.FloatMeasurement, RDF.type, SIO.MeasurementValue), self.app.db)

    def test_disjoint_union(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <-------  Disjoint Union ------- 
sio:BiologicalEntity  rdf:type owl:Class ;
    rdfs:label "biological entity" ;
    rdfs:subClassOf sio:HeterogeneousSubstance ;
    dct:description "A biological entity is a heterogeneous substance that contains genomic material or is the product of a biological process." .

sio:HeterogeneousSubstance  rdf:type owl:Class ;
    rdfs:label "heterogeneous substance" ;
    rdfs:subClassOf sio:MaterialEntity ;
    rdfs:subClassOf sio:ChemicalEntity ;
    dct:description "A heterogeneous substance is a chemical substance that is composed of more than one different kind of component." .

sio:MaterialEntity  rdf:type owl:Class ;
    rdfs:label "material entity" ;
    rdfs:subClassOf sio:Object ;
    dct:description "A material entity is a physical entity that is spatially extended, exists as a whole at any point in time and has mass." .

sio:ChemicalEntity  rdf:type owl:Class ;
    rdfs:label "chemical entity" ;
    rdfs:subClassOf sio:MaterialEntity ;
    dct:description "A chemical entity is a material entity that pertains to chemistry." .

ex:Lobe rdf:type owl:Class ;
    rdfs:subClassOf sio:BiologicalEntity ;
    rdfs:label "lobe" ;
    dct:description "A lobe that is part the brain." ;
    owl:equivalentClass 
        [ rdf:type owl:Class ;
            owl:disjointUnionOf ( ex:FrontalLobe ex:ParietalLobe ex:TemporalLobe ex:OccipitalLobe ex:LimbicLobe ) ] .
# -------  Disjoint Union -------> 
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Disjoint Union"]
        agent.process_graph(self.app.db)
        self.assertIn((ONT.FrontalLobe, RDFS.subClassOf, ONT.Lobe), self.app.db)
        self.assertIn((ONT.ParietalLobe, RDFS.subClassOf, ONT.Lobe), self.app.db)
        self.assertIn((ONT.TemporalLobe, RDFS.subClassOf, ONT.Lobe), self.app.db)
        self.assertIn((ONT.OccipitalLobe, RDFS.subClassOf, ONT.Lobe), self.app.db)
        self.assertIn((ONT.LimbicLobe, RDFS.subClassOf, ONT.Lobe), self.app.db)
        self.assertIn((ONT.FrontalLobe, OWL.disjointWith, ONT.ParietalLobe), self.app.db)
        self.assertIn((ONT.FrontalLobe, OWL.disjointWith, ONT.TemporalLobe), self.app.db)
        self.assertIn((ONT.FrontalLobe, OWL.disjointWith, ONT.OccipitalLobe), self.app.db)
        self.assertIn((ONT.FrontalLobe, OWL.disjointWith, ONT.LimbicLobe), self.app.db)
        self.assertIn((ONT.ParietalLobe, OWL.disjointWith, ONT.FrontalLobe), self.app.db)
        self.assertIn((ONT.ParietalLobe, OWL.disjointWith, ONT.TemporalLobe), self.app.db)
        self.assertIn((ONT.ParietalLobe, OWL.disjointWith, ONT.OccipitalLobe), self.app.db)
        self.assertIn((ONT.ParietalLobe, OWL.disjointWith, ONT.LimbicLobe), self.app.db)
        self.assertIn((ONT.TemporalLobe, OWL.disjointWith, ONT.FrontalLobe), self.app.db)
        self.assertIn((ONT.TemporalLobe, OWL.disjointWith, ONT.ParietalLobe), self.app.db)
        self.assertIn((ONT.TemporalLobe, OWL.disjointWith, ONT.OccipitalLobe), self.app.db)
        self.assertIn((ONT.TemporalLobe, OWL.disjointWith, ONT.LimbicLobe), self.app.db)
        self.assertIn((ONT.OccipitalLobe, OWL.disjointWith, ONT.FrontalLobe), self.app.db)
        self.assertIn((ONT.OccipitalLobe, OWL.disjointWith, ONT.ParietalLobe), self.app.db)
        self.assertIn((ONT.OccipitalLobe, OWL.disjointWith, ONT.TemporalLobe), self.app.db)
        self.assertIn((ONT.OccipitalLobe, OWL.disjointWith, ONT.LimbicLobe), self.app.db)
        self.assertIn((ONT.LimbicLobe, OWL.disjointWith, ONT.FrontalLobe), self.app.db)
        self.assertIn((ONT.LimbicLobe, OWL.disjointWith, ONT.ParietalLobe), self.app.db)
        self.assertIn((ONT.LimbicLobe, OWL.disjointWith, ONT.TemporalLobe), self.app.db)
        self.assertIn((ONT.LimbicLobe, OWL.disjointWith, ONT.OccipitalLobe), self.app.db)

    def test_object_intersection_of(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
# <------- Object Intersection Of ------- 
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
# ------- Object Intersection Of -------> 
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent1 =  config.Config["inferencers"]["Object Intersection Of One"]
        agent1.process_graph(self.app.db)
        agent2 =  config.Config["inferencers"]["Object Intersection Of Two"]
        agent2.process_graph(self.app.db)
        agent3 =  config.Config["inferencers"]["Object Intersection Of Three"]
        agent3.process_graph(self.app.db)
        self.assertIn((KB.ProteinReceptor, RDF.type, SIO.Target), self.app.db)
        self.assertIn((KB.Brian, RDF.type, ONT.FriendlyTalkingDog), self.app.db)

#    def test_data_intersection_of(self):
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
#''', format="turtle")
#        self.app.nanopub_manager.publish(*[np])
#        agent =  config.Config["inferencers"]["Data Intersection Of"]
#        agent.process_graph(self.app.db)
#        self.assertIn((KB.ReplaceMe, RDF.type, OWL.Nothing), self.app.db)
