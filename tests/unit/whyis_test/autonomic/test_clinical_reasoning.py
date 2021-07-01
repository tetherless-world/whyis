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
ONT = Namespace("http://purl.org/twc/HEALS/ont/")
KB = Namespace("http://purl.org/twc/HEALS/kb/")
SETS = Namespace("http://purl.org/ontology/sets/ont#")
WHYIS = Namespace("http://vocab.rpi.edu/whyis/")

prefixes = '''
@prefix heals: <http://purl.org/twc/HEALS/ont/> .
@prefix heals-kb: <http://purl.org/twc/HEALS/kb/> .
@prefix icdo: <http://purl.obolibrary.org/obo/icdo.owl#ICDO_>.
@prefix ogms: <http://purl.obolibrary.org/obo/OGMS_>.
@prefix bfo: <http://purl.obolibrary.org/obo/BFO_>.
@prefix scto: <https://bioportal.bioontology.org/ontologies/SCTO#SCTO_>.
@prefix dto: <https://bioportal.bioontology.org/ontologies/SCTO#DTO:>.
@prefix loinc: <http://purl.bioontology.org/ontology/LNC/>.
@prefix rxnorm: <http://purl.bioontology.org/ontology/RXNORM/>.
@prefix fhir: <http://hl7.org/fhir/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sct: <http://snomed.info/sct/>.
@prefix sio: <http://semanticscience.org/resource/>.
@prefix uo: <http://purl.obolibrary.org/obo/UO_>.
'''

patient_rdf = '''
heals-kb:P000001 a fhir:Patient;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P000001"];
    fhir:Patient.active [ fhir:value "true"^^xsd:boolean];
    fhir:Patient.name [
        fhir:index 0;
        fhir:HumanName.use [ fhir:value "official" ];
        fhir:HumanName.family [ fhir:value "Smith" ];
        fhir:HumanName.given [
            fhir:value "Mary";
            fhir:index 0
        ]
    ];
    fhir:Patient.gender [ fhir:value "female"];
    fhir:Patient.birthDate [
        fhir:value "1976-09-01"^^xsd:date ;
        fhir:Element.extension [
            fhir:index 0;
            # fhir:Extension.url [ fhir:value "http://hl7.org/fhir/StructureDefinition/patient-birthTime" ];
            fhir:Extension.valueDateTime [ fhir:value "1976-09-01T15:11:00+01:00"^^xsd:dateTime ]
        ]
    ];
    fhir:Patient.deceasedBoolean [ fhir:value "false"^^xsd:boolean];
    fhir:Patient.address [
         fhir:index 0;
         fhir:Address.use [ fhir:value "home" ];
         fhir:Address.type [ fhir:value "both" ];
         fhir:Address.line [
             fhir:value "225 Beverly Drive";
             fhir:index 0
         ];
         fhir:Address.city [ fhir:value "Los Angeles" ];
         fhir:Address.state [ fhir:value "CA" ];
         # fhir:Address.district [ fhir:value "..." ];
         fhir:Address.postalCode [ fhir:value "90210" ];
         fhir:Address.period [
             fhir:Period.start [ fhir:value "1980-11-15"^^xsd:date ]
         ]
    ];
    fhir:Patient.maritalStatus [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             # fhir:Coding.system [ fhir:value "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus" ];
             fhir:Coding.code [ fhir:value "M" ];
             fhir:Coding.display [ fhir:value "Married" ]
         ]
    ];
    fhir:Patient.telecom [
         fhir:index 0;
         fhir:ContactPoint.use [ fhir:value "home" ]
    ], [
         fhir:index 1;
         fhir:ContactPoint.system [ fhir:value "phone" ];
         fhir:ContactPoint.value [ fhir:value "5436792531" ];
         fhir:ContactPoint.use [ fhir:value "work" ]
    ] .


heals-kb:P000001-weight-1 a fhir:Observation;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P000001-weight-1"];
    fhir:Observation.status [ fhir:value "final"];
    fhir:Observation.category [
         fhir:index 0;
         fhir:CodeableConcept.coding [
             fhir:index 0;
             fhir:Coding.system [ fhir:value "http://terminology.hl7.org/CodeSystem/observation-category" ];
             fhir:Coding.code [ fhir:value "vital-signs" ];
             fhir:Coding.display [ fhir:value "Vital Signs" ]
         ]
    ];
    fhir:Observation.code [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             a loinc:29463-7;
             fhir:Coding.system [ fhir:value "http://loinc.org" ];
             fhir:Coding.code [ fhir:value "29463-7" ];
             fhir:Coding.display [ fhir:value "Body Weight" ]
         ]
    ];
    fhir:Observation.subject [
         fhir:link heals-kb:P000001;
         fhir:Reference.reference [ fhir:value "P000001" ]
    ];
    fhir:Observation.encounter [
         fhir:link heals-kb:P000001-visit-1;
         fhir:Reference.reference [ fhir:value "P000001-visit-1" ]
    ];
    fhir:Observation.effectiveDateTime [ fhir:value "2019-03-17"^^xsd:date];
    fhir:Observation.valueQuantity [
         fhir:Quantity.value [ fhir:value "225"^^xsd:decimal ];
         fhir:Quantity.unit [ fhir:value "lb" ];
         fhir:Quantity.system [ fhir:value "http://purl.obolibrary.org/obo/UO_" ];
         fhir:Quantity.code [ fhir:value "0010034" ]
    ] .

heals-kb:P000001-weight-2 a fhir:Observation;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P000001-weight-2"];

    fhir:Observation.status [ fhir:value "final"];
    fhir:Observation.category [
         fhir:index 0;
         fhir:CodeableConcept.coding [
             fhir:index 0;
             fhir:Coding.system [ fhir:value "http://terminology.hl7.org/CodeSystem/observation-category" ];
             fhir:Coding.code [ fhir:value "vital-signs" ];
             fhir:Coding.display [ fhir:value "Vital Signs" ]
         ]
    ];
    fhir:Observation.code [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             a loinc:29463-7;
             fhir:Coding.system [ fhir:value "http://loinc.org" ];
             fhir:Coding.code [ fhir:value "29463-7" ];
             fhir:Coding.display [ fhir:value "Body Weight" ]
         ]
    ];
    fhir:Observation.subject [
         fhir:link heals-kb:P000001;
         fhir:Reference.reference [ fhir:value "P000001" ]
    ];
    fhir:Observation.encounter [
         fhir:link heals-kb:P000001-visit-2;
         fhir:Reference.reference [ fhir:value "P000001-visit-2" ]
    ];
    fhir:Observation.effectiveDateTime [ fhir:value "2019-04-21"^^xsd:date];
    fhir:Observation.valueQuantity [
         fhir:Quantity.value [ fhir:value "246"^^xsd:decimal ];
         fhir:Quantity.unit [ fhir:value "lb" ];
         fhir:Quantity.system [ fhir:value "http://purl.obolibrary.org/obo/UO_" ];
         fhir:Quantity.code [ fhir:value "0010034" ]
    ] .

heals-kb:P000001-visit-1 a fhir:Encounter ;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P000001-visit-1"] ;
    fhir:Encounter.status [ fhir:value "finished"] ; 
    fhir:Encounter.subject [
         fhir:link heals-kb:P000001 ;
         fhir:Reference.reference [ fhir:value "P000001" ]
    ];
    fhir:Encounter.period [
         fhir:Period.start [ fhir:value "2019-03-17T16:00:00"^^xsd:dateTime ];
         fhir:Period.end [ fhir:value "2019-03-17T16:30:00"^^xsd:dateTime ]
    ].

heals-kb:P000001-visit-2 a fhir:Encounter ;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P000001-visit-2"];
    fhir:Encounter.status [ fhir:value "finished"];
    fhir:Encounter.subject [
         fhir:link heals-kb:P000001;
         fhir:Reference.reference [ fhir:value "P000001" ]
    ];
    fhir:Encounter.period [
         fhir:Period.start [ fhir:value "2019-04-21T16:00:00"^^xsd:dateTime ];
         fhir:Period.end [ fhir:value "2019-04-21T16:30:00"^^xsd:dateTime ]
    ].
'''

class ClinincalReasoningTestCase(AgentUnitTestCase):
    def test_weight_gain(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf, format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Weight Gain"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.WeightGain))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_clinically_relevant_weight_gain(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf, format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Clinically Relevant Weight Gain"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.ClinicallyRelevantWeightGain))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_bmi_gain(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:P00000A a fhir:Patient .

heals-kb:P00000A-bmi-1 a fhir:Observation;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-bmi-1"];
    fhir:Observation.status [ fhir:value "final"];
    fhir:Observation.category [
         fhir:index 0;
         fhir:CodeableConcept.coding [
             fhir:index 0;
             fhir:Coding.system [ fhir:value "http://terminology.hl7.org/CodeSystem/observation-category" ];
             fhir:Coding.code [ fhir:value "vital-signs" ];
             fhir:Coding.display [ fhir:value "Vital Signs" ]
         ]
    ];
    fhir:Observation.code [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             a loinc:35925-4;
             fhir:Coding.system [ fhir:value "http://loinc.org" ];
             fhir:Coding.code [ fhir:value "35925-4" ];
             fhir:Coding.display [ fhir:value "Body Mass Index" ]
         ]
    ];
    fhir:Observation.subject [
         fhir:link heals-kb:P00000A;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Observation.encounter [
         fhir:link heals-kb:P00000A-visit-1;
         fhir:Reference.reference [ fhir:value "P00000A-visit-1" ]
    ];
    fhir:Observation.effectiveDateTime [ fhir:value "2019-06-01"^^xsd:date];
    fhir:Observation.valueQuantity [
         fhir:Quantity.value [ fhir:value "26"^^xsd:decimal ];
         fhir:Quantity.unit [ fhir:value "kg/m^2" ];
         fhir:Quantity.system [ fhir:value "http://purl.obolibrary.org/obo/UO_" ];
         fhir:Quantity.code [ fhir:value "0000086" ]
    ] .

heals-kb:P00000A-bmi-3 a fhir:Observation;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-bmi-3"];

    fhir:Observation.status [ fhir:value "final"];
    fhir:Observation.category [
         fhir:index 0;
         fhir:CodeableConcept.coding [
             fhir:index 0;
             fhir:Coding.system [ fhir:value "http://terminology.hl7.org/CodeSystem/observation-category" ];
             fhir:Coding.code [ fhir:value "vital-signs" ];
             fhir:Coding.display [ fhir:value "Vital Signs" ]
         ]
    ];
    fhir:Observation.code [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             a loinc:35925-4;
             fhir:Coding.system [ fhir:value "http://loinc.org" ];
             fhir:Coding.code [ fhir:value "35925-4" ];
             fhir:Coding.display [ fhir:value "Body Mass Index" ]
         ]
    ];
    fhir:Observation.subject [
         fhir:link heals-kb:P00000A;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Observation.encounter [
         fhir:link heals-kb:P00000A-visit-3;
         fhir:Reference.reference [ fhir:value "P00000A-visit-3" ]
    ];
    fhir:Observation.effectiveDateTime [ fhir:value "2019-06-15"^^xsd:date];
    fhir:Observation.valueQuantity [
         fhir:Quantity.value [ fhir:value "28"^^xsd:decimal ];
         fhir:Quantity.unit [ fhir:value "kg/m^2" ];
         fhir:Quantity.system [ fhir:value "http://purl.obolibrary.org/obo/UO_" ];
         fhir:Quantity.code [ fhir:value "0000086" ]
    ] .

heals-kb:P00000A-visit-1 a fhir:Encounter ;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-visit-1"] ;
    fhir:Encounter.status [ fhir:value "finished"] ; 
    fhir:Encounter.subject [
         fhir:link heals-kb:P00000A ;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Encounter.period [
         fhir:Period.start [ fhir:value "2019-06-01T16:00:00"^^xsd:dateTime ];
         fhir:Period.end [ fhir:value "2019-06-01T16:30:00"^^xsd:dateTime ]
    ].

heals-kb:P00000A-visit-3 a fhir:Encounter ;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-visit-3"] ;
    fhir:Encounter.status [ fhir:value "finished"] ; 
    fhir:Encounter.subject [
         fhir:link heals-kb:P00000A ;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Encounter.period [
         fhir:Period.start [ fhir:value "2019-06-15T16:00:00"^^xsd:dateTime ];
         fhir:Period.end [ fhir:value "2019-06-15T16:30:00"^^xsd:dateTime ]
    ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["BMI Gain"]
        agent.process_graph(self.app.db)
        bmi_gain_subject = list(self.app.db.subjects(RDF.type, ONT.BMIGain))
        self.assertEquals(len(bmi_gain_subject), 1)
        for subject in bmi_gain_subject :
            self.assertIn((KB.P00000A, SIO.hasAttribute, subject), self.app.db)


    def test_step_count_decrease(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:P00000A a fhir:Patient .

heals-kb:P00000A-stepcount-1 a fhir:Observation;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-stepcount-1"];
    fhir:Observation.status [ fhir:value "final"];
    fhir:Observation.category [
         fhir:index 0;
         fhir:CodeableConcept.coding [
             fhir:index 0;
             fhir:Coding.system [ fhir:value "http://snomed.info/sct" ];
             fhir:Coding.code [ fhir:value "68130003" ];
             fhir:Coding.display [ fhir:value "Physical activity (observable entity)" ]
         ]
    ];
    fhir:Observation.code [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             a loinc:55423-8;
             fhir:Coding.system [ fhir:value "http://loinc.org" ];
             fhir:Coding.code [ fhir:value "55423-8" ];
             fhir:Coding.display [ fhir:value "Number of steps in unspecified time Pedometer" ]
         ]
    ];
    fhir:Observation.subject [
         fhir:link heals-kb:P00000A;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Observation.encounter [
         fhir:link heals-kb:P00000A-visit-1;
         fhir:Reference.reference [ fhir:value "P00000A-visit-1" ]
    ];
    fhir:Observation.effectiveDateTime [ fhir:value "2019-06-01"^^xsd:date];
    fhir:Observation.valueQuantity [
         fhir:Quantity.value [ fhir:value "8000"^^xsd:decimal ];
         fhir:Quantity.unit [ fhir:value "steps/day" ];
         fhir:Quantity.system [ fhir:value "http://unitsofmeasure.org/" ];
         fhir:Quantity.code [ fhir:value "{steps}/d" ]
    ] .


heals-kb:P00000A-stepcount-3 a fhir:Observation;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-stepcount-3"];
    fhir:Observation.status [ fhir:value "final"];
    fhir:Observation.category [
         fhir:index 0;
         fhir:CodeableConcept.coding [
             fhir:index 0;
             fhir:Coding.system [ fhir:value "http://snomed.info/sct" ];
             fhir:Coding.code [ fhir:value "68130003" ];
             fhir:Coding.display [ fhir:value "Physical activity (observable entity)" ]
         ]
    ];
    fhir:Observation.code [
         fhir:CodeableConcept.coding [
             fhir:index 0;
             a loinc:55423-8;
             fhir:Coding.system [ fhir:value "http://loinc.org" ];
             fhir:Coding.code [ fhir:value "55423-8" ];
             fhir:Coding.display [ fhir:value "Number of steps in unspecified time Pedometer" ]
         ]
    ];
    fhir:Observation.subject [
         fhir:link heals-kb:P00000A;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Observation.encounter [
         fhir:link heals-kb:P00000A-visit-3;
         fhir:Reference.reference [ fhir:value "P00000A-visit-3" ]
    ];
    fhir:Observation.effectiveDateTime [ fhir:value "2019-06-15"^^xsd:date];
    fhir:Observation.valueQuantity [
         fhir:Quantity.value [ fhir:value "4000"^^xsd:decimal ];
         fhir:Quantity.unit [ fhir:value "steps/day" ];
         fhir:Quantity.system [ fhir:value "http://unitsofmeasure.org/" ];
         fhir:Quantity.code [ fhir:value "{steps}/d" ]
    ] .


heals-kb:P00000A-visit-1 a fhir:Encounter ;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-visit-1"] ;
    fhir:Encounter.status [ fhir:value "finished"] ; 
    fhir:Encounter.subject [
         fhir:link heals-kb:P00000A ;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Encounter.period [
         fhir:Period.start [ fhir:value "2019-06-01T16:00:00"^^xsd:dateTime ];
         fhir:Period.end [ fhir:value "2019-06-01T16:30:00"^^xsd:dateTime ]
    ].

heals-kb:P00000A-visit-3 a fhir:Encounter ;
    fhir:nodeRole fhir:treeRoot;
    fhir:Resource.id [ fhir:value "P00000A-visit-3"] ;
    fhir:Encounter.status [ fhir:value "finished"] ; 
    fhir:Encounter.subject [
         fhir:link heals-kb:P00000A ;
         fhir:Reference.reference [ fhir:value "P00000A" ]
    ];
    fhir:Encounter.period [
         fhir:Period.start [ fhir:value "2019-06-15T16:00:00"^^xsd:dateTime ];
         fhir:Period.end [ fhir:value "2019-06-15T16:30:00"^^xsd:dateTime ]
    ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Step Count Decrease"]
        agent.process_graph(self.app.db)
        step_count_subject = list(self.app.db.subjects(RDF.type, ONT.ReductionInSteps))
        self.assertEquals(len(step_count_subject), 1)
        for subject in step_count_subject :
            self.assertIn((KB.P00000A, SIO.hasAttribute, subject), self.app.db)

    def test_decreased_activity_hypothesis(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Decreased Activity Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.DecreasedActivityHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)


    def test_change_of_diet_hypothesis(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Change Of Diet Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.ChangeOfDietHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)


    def test_medicinal_effect_hypothesis(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Medicinal Effect Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.MedicinalEffectHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)


    def test_biological_effect_hypothesis(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Biological Effect Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.BiologicalEffectHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)

    def test_metabolism_decrease_hypothesis(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Biological Effect Hypothesis"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Metabolism Decrease Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.MetabolismDecreaseHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)


    def test_hypothyroidism_hypothesis(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Biological Effect Hypothesis"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Metabolism Decrease Hypothesis"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Hypothyroidism Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.HypothyroidismHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)

    def test_single_drug_side_effect_hypothesis(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Medicinal Effect Hypothesis"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Single Drug Side Effect Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.SingleDrugSideEffectHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)

    def test_multiple_drug_contraindication_hypothesis(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Medicinal Effect Hypothesis"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Multiple Drug Contraindication Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.MultipleDrugContraindicationHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)


    def test_reduction_in_steps_hypothesis(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Decreased Activity Hypothesis"]
        agent.process_graph(self.app.db)
        agent =  config.Config["inferencers"]["Reduction In Steps Hypothesis"]
        agent.process_graph(self.app.db)
        hypothesis_subject = list(self.app.db.subjects(RDF.type, ONT.ReductionInStepsHypothesis))
        self.assertEquals(len(hypothesis_subject), 1)




    def test_truth_propagation(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ;
            sio:hasStartTime "2019-03-17"^^xsd:date ;
            sio:hasEndTime "2019-04-21"^^xsd:date ;
            heals:hypothesis (
                heals-kb:BiologicalEffectHypothesis heals-kb:MetabolismDecreaseHypothesis
            ) ] .

     heals-kb:BiologicalEffectHypothesis rdf:type heals:BiologicalEffectHypothesis ;
        sio:hasStartTime "2019-03-17"^^xsd:date ;
        sio:hasEndTime "2019-04-21"^^xsd:date ;
        heals:hasTruthValue [ rdf:type heals:Unknown ] . 

     heals-kb:MetabolismDecreaseHypothesis rdf:type heals:MetabolismDecreaseHypothesis ;
        sio:hasStartTime "2019-03-17"^^xsd:date ;
        sio:hasEndTime "2019-04-21"^^xsd:date ;
        heals:hasTruthValue [ rdf:type heals:True ] ;
        sio:inRelationTo heals-kb:BiologicalEffectHypothesis . 

''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Truth Propagation"]
        agent.process_graph(self.app.db)
        true_hypotheses = list(self.app.db.subjects(RDF.type, URIRef("http://purl.org/twc/HEALS/ont/True")))
        self.assertEquals(len(true_hypotheses), 2)

    def test_decreased_activity(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:DecreasedActivity ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Decreased Activity"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.ClinicallyRelevantWeightGain))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_medicinal_effect(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MedicinalEffect ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Medicinal Effect"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.ClinicallyRelevantWeightGain))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_biological_effect(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:BiologicalEffect ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Biological Effect"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.ClinicallyRelevantWeightGain))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_change_of_diet(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ChangeOfDiet ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Change Of Diet"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.ClinicallyRelevantWeightGain))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)


    def test_reduction_in_steps(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ReductionInSteps ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Reduction In Steps"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.DecreasedActivity))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)


    def test_single_drug_side_effect(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:SingleDrugSideEffect ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Single Drug Side Effect"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.MedicinalEffect))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)


    def test_multiple_drug_contraindication(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MultipleDrugContraindication ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Multiple Drug Contraindication"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.MedicinalEffect))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)


    def test_metabolism_decrease(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MetabolismDecrease ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Metabolism Decrease"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.BiologicalEffect))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_hypothyroidism(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+patient_rdf + '''
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:Hypothyroidism ] .
''', format="turtle")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Hypothyroidism"]
        agent.process_graph(self.app.db)
        weight_gain_subject = list(self.app.db.subjects(RDF.type, ONT.MetabolismDecrease))
        self.assertEquals(len(weight_gain_subject), 1)
        for subject in weight_gain_subject :
            self.assertIn((KB.P000001, SIO.hasAttribute, subject), self.app.db)

    def test_decreased_activity_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:DecreasedActivity ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Decreased Activity Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.DecreasedActivityRule))
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_biological_effect_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:BiologicalEffect ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Biological Effect Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.BiologicalEffectRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_medicinal_effect_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MedicinalEffect ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Medicinal Effect Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects( RDF.type, ONT.MedicinalEffectRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_change_of_diet_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ChangeOfDiet ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ClinicallyRelevantWeightGain ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Change Of Diet Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.ChangeOfDietRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_metabolism_decrease_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MetabolismDecrease ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:BiologicalEffect ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Metabolism Decrease Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.MetabolismDecreaseRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_hypothyroidism_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:Hypothyroidism ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MetabolismDecrease ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Hypothyroidism Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.HypothyroidismRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_single_drug_side_effect_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:SingleDrugSideEffect ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MedicinalEffect ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Single Drug Side Effect Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.SingleDrugSideEffectRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_multiple_drug_contraindication_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MultipleDrugContraindication ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:MedicinalEffect ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Multiple Drug Contraindication Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.MultipleDrugContraindicationRule) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)

    def test_reduction_in_steps_back_tracer(self):
        self.dry_run = False
        np = nanopub.Nanopublication()
        np.assertion.parse(data=prefixes+'''
heals-kb:Assertion_1 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:ReductionInSteps ] .
}

heals-kb:Assertion_2 {
    heals-kb:P000001 sio:hasAttribute 
        [ a heals:DecreasedActivity ] .
}
''', format="trig")
        self.app.nanopub_manager.publish(*[np])
        agent =  config.Config["inferencers"]["Reduction In Steps Back Tracer"]
        agent.process_graph(self.app.db)
        hypothesis = list( self.app.db.subjects(RDF.type, ONT.ReductionInStepsRule ) )
        self.assertEquals(len(hypothesis), 1)
        for hyp in hypothesis :
            self.assertIn((KB.Assertion_2, SETS.hypothesis, hyp), self.app.db)
