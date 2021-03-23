# -*- config:utf-8 -*-

import importer
from whyis import autonomic
import logging

from datetime import datetime, timedelta

project_name = "whyis"

# Set to be custom for your project
LOD_PREFIX = 'http://localhost:5000'
#os.getenv('lod_prefix') if os.getenv('lod_prefix') else 'http://hbgd.tw.rpi.edu'

# from whyis.namespace import skos

InferenceRules = dict(
    Class_Disjointness = {
        "reference" : "Class Disjointness",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class .
    ?resource rdf:type ?disjointClass .
    { ?class owl:disjointWith ?disjointClass . } 
        UNION
    { ?disjointClass owl:disjointWith ?class . }''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{class}} is a disjoint with {{disjointClass}}, any resource that is an instance of {{class}} is not an instance of {{disjointClass}}. Therefore, since {{resource}} is an instance of {{class}}, it can not be an instance of {{disjointClass}}."
    },
    Object_Property_Transitivity = {
        "reference" : "Object Property Transitivity",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?transitiveProperty ?o1 .
    ?o1  ?transitiveProperty ?o2 .
    ?transitiveProperty rdf:type owl:TransitiveProperty .''',
        "consequent" : "?resource ?transitiveProperty ?o2 .",
        "explanation" : "Since {{transitiveProperty}} is a transitive object property, and the relationships {{resource}} {{transitiveProperty}} {{o1}} and {{o1}} {{transitiveProperty}} {{o2}} exist, then we can infer that {{resource}} {{transitiveProperty}} {{o2}}."
    },
    Object_Property_Reflexivity = {
        "reference" : "Object Property Reflexivity",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?type ;
        ?reflexiveProperty ?o .
    ?o rdf:type ?type.
    ?reflexiveProperty rdf:type owl:ReflexiveProperty .''',
        "consequent" : "?resource ?reflexiveProperty ?resource .",
        "explanation" : "Since {{resource}} has a {{reflexiveProperty}} assertion to {{o}}, {{resource}} and {{o}} are both of type {{type}}, and {{reflexiveProperty}} is a reflexive property, we can infer that {{resource}} {{reflexiveProperty}} {{resource}}."
    },
    Property_Domain = {
        "reference" : "Property Domain",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?p ?o .
    ?p rdfs:domain ?class .''',
        "consequent" : "?resource rdf:type ?class .",
        "explanation" : "Since the domain of {{p}} is {{class}}, this implies that {{resource}} is a {{class}}."
    },
    Property_Range = {
        "reference" : "Property Range",
        "resource" : "?resource",
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?p ?o .
    ?p rdfs:range ?class .''',
        "consequent" : "?o rdf:type ?class .",
        "explanation" : "Since the range of {{p}} is {{class}}, this implies that {{o}} is a {{class}}."
    },
    Functional_Data_Property = {
        "reference" : "Functional Data Property",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?functionalProperty ?o1 ,
            ?o2 .
    ?functionalProperty rdf:type owl:DatatypeProperty ,
            owl:FunctionalProperty .
    FILTER (str(?o1) !=  str(?o2))''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{functionalProperty}} is a functional data property, {{resource}} can only have one value for {{functionalProperty}}. Since {{resource}} {{functionalProperty}} both {{o1}} and {{o2}}, and {{o1}} is different from {{o2}}, an inconsistency occurs."
    },
    Functional_Object_Property = {
        "reference" : "Functional Object Property",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?functionalProperty ?o1 ,
            ?o2 .
    ?functionalProperty rdf:type owl:ObjectProperty , 
            owl:FunctionalProperty .
    FILTER (str(?o1) !=  str(?o2))''',
        "consequent" : "?o1 owl:sameAs ?o2 .",
        "explanation" : "Since {{functionalProperty}} is a functional object property, {{resource}} can only have one value for {{functionalProperty}}. Since {{resource}} {{functionalProperty}} both {{o1}} and {{o2}}, we can infer that {{o1}} and {{o2}} must be the same individual."
    },
    Property_Disjointness = {
        "reference" : "Property Disjointness",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?p1 ?o1 ,
            ?o2 .
    ?resource ?p2 ?o2.
    {?p1 owl:propertyDisjointWith ?p2 .}
        UNION
    {?p2 owl:propertyDisjointWith ?p1 .}''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since properties {p1} and {p2} are disjoint, {{resource}} having both {{p2}} {{o2}} as well as {{p1}} {{o2}} leads to an inconsistency. "
    },
    Object_Property_Asymmetry = {
        "reference" : "Object Property Asymmetry",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?asymmetricProperty ?o .
    ?asymmetricProperty rdf:type owl:AsymmetricProperty .
    ?o ?asymmetricProperty ?resource .''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{asymmetricProperty}} is an asymmetric property, and {{resource}} {{asymmetricProperty}} {{o}}, then the assertion {{o}} {{asymmetricProperty}} {{resource}} results in an inconsistency."
    },
    Object_Property_Symmetry = {
        "reference" : "Object Property Symmetry",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?symmetricProperty ?o .
    ?symmetricProperty rdf:type owl:SymmetricProperty .''',
        "consequent" : "?o ?symmetricProperty ?resource .",
        "explanation" : "Since {{symmetricProperty}} is a symmetric property, and {{resource}} {{symmetricProperty}} {{o}}, we can infer that {{o}} {{symmetricProperty}} {{resource}}."
    },
    Object_Property_Irreflexivity = {
        "reference" : "Object Property Irreflexivity",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?irreflexiveProperty ?o .
    ?irreflexiveProperty rdf:type owl:IrreflexiveProperty .
    ?resource ?irreflexiveProperty ?resource .''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{resource}} has a {{irreflexiveProperty}} assertion, and {{irreflexiveProperty}} is a irreflexive property, we can infer that the relationship {{resource}} {{irreflexiveProperty}} {{resource}} does not exist."
    },
    Class_Inclusion = {
        "reference" : "Class Inclusion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdfs:subClassOf ?class .
    ?class rdfs:subClassOf+ ?superClass .''',
        "consequent" : "?resource rdfs:subClassOf ?superClass .",
        "explanation" : "Since {{class}} is a subclass of {{superClass}}, any class that is a subclass of {{class}} is also a subclass of {{superClass}}. Therefore, {{resource}} is a subclass of {{superClass}}."
    },
    Individual_Inclusion = {
        "reference" : "Individual Inclusion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class .
    ?class rdfs:subClassOf+ ?superClass .''',
        "consequent" : "?resource rdf:type ?superClass .",
        "explanation" : "Any instance of {{class}} is also an instance of {{superClass}}. Therefore, since {{resource}} is a {{class}}, it also is a {{superClass}}."
    },
    Property_Inclusion = {
        "reference" : "Property Inclusion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o .
    ?p rdf:type owl:Property ;
        rdfs:subPropertyOf+ ?superProperty .''',
        "consequent" : "?resource ?superProperty ?o .",
        "explanation" : "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
    },
    Object_Property_Inclusion = {
        "reference" : "Object Property Inclusion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o .
    ?p rdf:type owl:ObjectProperty ;
        rdfs:subPropertyOf+ ?superProperty .''',
        "consequent" : "?resource ?superProperty ?o .",
        "explanation" : "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
    },
    Data_Property_Inclusion = {
        "reference" : "Data Property Inclusion",
        "resource" : "?resource",
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o .
    ?p rdf:type owl:DatatypeProperty ;
        rdfs:subPropertyOf+ ?superProperty .''',
        "consequent" : "?resource ?superProperty ?o .",
        "explanation" : "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
    },
    Class_Equivalence = {
        "reference" : "Class Equivalence",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource rdf:type ?superClass.
    {?superClass owl:equivalentClass ?equivClass .}
        UNION
    {?equivClass owl:equivalentClass ?superClass .}''', 
        "consequent" : "?resource rdf:type ?equivClass .",
        "explanation" : "{{superClass}} is equivalent to {{equivClass}}, so since {{resource}} is a {{superClass}}, it is also a {{equivClass}}."
    },
    Property_Equivalence = {
        "reference" : "Property Equivalence",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o .
    {?p owl:equivalentProperty ?equivProperty .}
        UNION
    {?equivProperty owl:equivalentProperty ?p . }''', 
        "consequent" : "?resource ?equivProperty ?o .",
        "explanation" : "The properties {{p}} and {{equivProperty}} are equivalent. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{equivProperty}} {{o}}."
    },
    Object_Property_Inversion = {
        "reference" : "Object Property Inversion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o .
    ?p rdf:type owl:ObjectProperty .
    {?p owl:inverseOf ?inverseProperty .}
        UNION
    {?inverseProperty owl:inverseOf ?p .}''', 
        "consequent" : "?o ?inverseProperty ?resource .",
        "explanation" : "The object properties {{p}} and {{inverseProperty}} are inversely related to eachother. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{o}} {{inverseProperty}} {{resource}}."
    },
    Same_Individual = {
        "reference" : "Same Individual",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    {
        ?resource owl:sameAs ?individual .
    }
        UNION
    {
        ?individual owl:sameAs ?resource .
    }
    ?resource ?p ?o .''', 
        "consequent" : "?individual ?p ?o .",
        "explanation" : "Since {{resource}} is the same as {{individual}}, they share the same properties."#except maybe for annotation properties? should possibly add this check in
    },
    Different_Individuals = {
        "reference" : "Different Individuals",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    {
        ?resource owl:differentFrom ?individual .
    }
        UNION
    {
        ?individual owl:differentFrom ?resource .
    }
    ?resource owl:sameAs ?individual .''', 
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{resource}} is asserted as being different from {{individual}}, the assertion that {{resource}} is the same as {{individual}} leads to an inconsistency."
    },
    All_Different_Individuals = {
        "reference" : "All Different Individuals",
        "resource" : "?restriction", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?restriction rdf:type owl:AllDifferent ;
        owl:distinctMembers ?list .
    ?list rdf:rest*/rdf:first ?member .
    {
        SELECT DISTINCT ?item ?restrict WHERE
        {
            ?restrict rdf:type owl:AllDifferent ;
                owl:distinctMembers ?list .
            ?list rdf:rest*/rdf:first ?item .
        }
    }
    BIND(?restriction AS ?restrict) 
    FILTER(?member != ?item)''', 
        "consequent" : "?member owl:differentFrom ?item .",
        "explanation" : "Since {{restriction}} is an all different restriction with individuals listed in {{list}}, each member in {{list}} is different from each other member in the list."
    },
    Class_Assertion = {
        "reference" : "Class Assertion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource rdf:type ?class .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf+ ?superClass .''', 
        "consequent" : "?resource rdf:type ?superClass .",
        "explanation" : "Since {{class}} is a subclass of {{superClass}}, any individual that is an instance of {{class}} is also an instance of {{superClass}}. Therefore, {{resource}} is an instance of {{superClass}}."
    },
#        Positive_Object_Property_Assertion = {
#            "reference" : "Positive Object Property Assertion",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
#            "antecedent" :  '''
#    ?resource ?objectProperty ?o.
#    ?objectProperty rdf:type owl:ObjectProperty .
#    ?class rdf:type owl:Class;
#        rdfs:subClassOf|owl:equivalentClass
#            [ rdf:type owl:Restriction ;
#                owl:onProperty ?objectProperty ;
#                owl:someValuesFrom owl:Thing ] .''',#may need to come back to this 
#            "consequent" : "?resource rdf:type ?class .",
#            "explanation" : "Since {{resource}} {{objectProperty}} {{o}}, and {{class}} has an object property restriction on {{objectProperty}} to have any value that is an owl:Thing, we can infer that {{resource}} is a {{class}}."
#        },
#        Positive_Data_Property_Assertion = { # Need to revisit to include data ranges
#            "reference" : "Positive Data Property Assertion",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
#            "antecedent" :  '''
#    ?resource ?dataProperty ?o.
#    ?dataProperty rdf:type owl:DatatypeProperty .
#    ?class rdf:type owl:Class;
#        rdfs:subClassOf|owl:equivalentClass
#            [ rdf:type owl:Restriction ;
#                owl:onProperty ?dataProperty ;
#                owl:someValuesFrom ?value ] .
#    FILTER(DATATYPE(?o) = ?value)''', 
#            "consequent" : "?resource rdf:type ?class .",
#            "explanation" : "Since {{resource}} {{dataProperty}} {{o}}, and {{class}} has an object property restriction on {{dataProperty}} to have a value of type {{value}}, and {{o}} is of type {{value}}, we can infer that {{resource}} is a {{class}}."
#        }, # the previous two might just be s p o assertion
    Negative_Object_Property_Assertion = {
        "reference" : "Negative Object Property Assertion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o.
    ?p rdf:type owl:ObjectProperty .
    ?x rdf:type owl:NegativePropertyAssertion ;
        owl:sourceIndividual ?resource ;
        owl:assertionProperty ?p ;
        owl:targetIndividual ?o .''', 
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since a negative object property assertion was made with source {{resource}}, object property {{p}}, and target individual {{o}}, the existence of {{resource}} {{p}} {{o}} results in an inconsistency."
    },
    Negative_Data_Property_Assertion = {
        "reference" : "Negative Data Property Assertion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
        "antecedent" :  '''
    ?resource ?p ?o.
    ?p rdf:type owl:DatatypeProperty .
    ?x rdf:type owl:NegativePropertyAssertion ;
        owl:sourceIndividual ?resource ;
        owl:assertionProperty ?p ;
        owl:targetValue ?o .''', 
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since a negative datatype property assertion was made with source {{resource}}, datatype property {{p}}, and target value {{o}}, the existence of {{resource}} {{p}} {{o}} results in an inconsistency."
    },
    Keys = {
        "reference" : "Keys",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?keyProperty ?keyValue.
    ?class rdf:type owl:Class ;
        owl:hasKey ( ?keyProperty ) .
    ?individual rdf:type ?class ;
        ?keyProperty ?keyValue.''',
        "consequent" : "?resource owl:sameAs ?individual .",
        "explanation" : "Since {{class}} has key {{keyProperty}}, {{resource}} and {{individual}} are both of type {{class}}, and {{resource}} and {{individual}} both {{keyProperty}} {{keyValue}}, then {{resource}} and {{individual}} must be the same."
    },
    Inverse_Functional_Object_Property = {
        "reference" : "Inverse Functional Object Property",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?invFunctionalProperty ?o .
    ?individual ?invFunctionalProperty ?o .
    ?invFunctionalProperty rdf:type owl:ObjectProperty ,
            owl:InverseFunctionalProperty .''',
        "consequent" : "?resource owl:sameAs ?individual",
        "explanation" : "Since {{invFunctionalProperty}} is an inverse functional property, and {{resource}} and {{individual}} both have the relationship {{invFunctionalProperty}} {{o}}, then we can infer that {{resource}} is the same as {{individual}}."
    },
    Object_Some_Values_From = {# Should revisit this after confirming test case
        "reference" : "Object Some Values From",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?objectProperty
        [ rdf:type ?valueclass ] .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction;
            owl:onProperty ?objectProperty;
            owl:someValuesFrom ?valueclass ] .''',
        "consequent" : "?resource rdf:type ?class .",
        "explanation" : "Since {{resource}} {{objectProperty}} an instance of {{valueclass}}, and {{class}} has a restriction on {{objectProperty}} to have some values from {{valueclass}}, we can infer that {{resource}} rdf:type {{class}}."
    },
    Data_Some_Values_From = {
        "reference" : "Data Some Values From",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?datatypeProperty ?val .
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?datatypeProperty ;
                owl:someValuesFrom ?value ] .
    FILTER(DATATYPE(?val) != ?value)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "{{resource}} {{datatypeProperty}} {{val}}, but {{val}} does not the same datatype {{value}} restricted for {{datatypeProperty}} in {{class}}. Since {{resource}} rdf:type {{class}}, an inconsistency occurs."
    },#Data some and all values from behave the same as each other..? May need to revisit
    Object_Has_Self = {
        "reference" : "Object Has Self",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:hasSelf \"true\"^^xsd:boolean ] .''',
        "consequent" : "?resource ?objectProperty ?resource .",
        "explanation" : "{{resource}} is of type {{class}}, which has a self restriction on the property {{objectProperty}}, allowing us to infer {{resource}} {{objectProperty}} {{resource}}."
    },
    Object_Has_Value = {
        "reference" : "Object Has Value",
        "resource" : "?resource",
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class .
    ?objectProperty rdf:type owl:ObjectProperty.
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:hasValue ?object ] .''',
        "consequent" : "?resource ?objectProperty?object .",
        "explanation" : "Since {{resource}} is of type {{class}}, which has a value restriction on {{objectProperty}} to have {{object}}, we can infer that {{resource}} {{objectProperty}} {{object}}."
    },
    Data_Has_Value = {
        "reference" : "Data Has Value",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?datatypeProperty ?value.
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?class owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?datatypeProperty ;
            owl:hasValue ?value ].''',
        "consequent" : "?resource rdf:type ?class .",
        "explanation" : "Since {{class}} is equivalent to the restriction on {{datatypeProperty}} to have value {{value}} and {{resource}} {{datatypeProperty}} {{value}}, we can infer that {{resource}} rdf:type {{class}}."
    },#Note that only owl:equivalentClass results in inference, not rdfs:subClassOf
    Object_One_Of_Membership = {
        "reference" : "Object One Of Membership",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type owl:Class ;
        owl:oneOf ?list .
    ?list rdf:rest*/rdf:first ?member .''',
        "consequent" : "?member rdf:type ?resource .",
        "explanation" : "Since {{resource}} has a one of relationship with {{list}}, the member {{member}} in {{list}} is of type {{resource}}."
    },
    Object_One_Of_Inconsistency = {
        "reference" : "Object One Of Inconsistency",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?class rdf:type owl:Class ;
        owl:oneOf ?list .
    ?list rdf:rest*/rdf:first ?member .
    ?resource rdf:type ?class .
    {
        SELECT DISTINCT (COUNT(DISTINCT ?concept) AS ?conceptCount) #?concept ?individual 
        WHERE 
        {
            ?concept rdf:type owl:Class ;
                owl:oneOf ?list .
            ?individual rdf:type ?concept .
            ?list rdf:rest*/rdf:first ?member .
            FILTER(?individual = ?member)
        }
    }
    FILTER(?conceptCount=0)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{class}} has a one of relationship with {{list}}, and {{resource}} is not in {{list}}, the assertion {{resource}} is a {{class}} leads to an inconsistency."# may need to revisit.. do we also check owl:differentFrom?
    },
    Data_One_Of = {
        "reference" : "Data One Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?datatypeProperty rdf:type owl:DatatypeProperty ;
        rdfs:range [ rdf:type owl:DataRange ;
            owl:oneOf ?list ] .
    ?resource ?datatypeProperty ?value .
    ?list rdf:rest*/rdf:first ?member .
    {
        SELECT DISTINCT (COUNT( DISTINCT ?datatypeProperty) AS ?dataCount) #?individual 
        WHERE 
        {
            ?datatypeProperty rdf:type owl:DatatypeProperty ;
            rdfs:range [ rdf:type owl:DataRange ;
                owl:oneOf ?list ] .
            ?individual ?datatypeProperty ?value .
            ?list rdf:rest*/rdf:first ?member .
            FILTER(?value=?member)
        }
    }
    FILTER(?dataCount=0)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{datatypeProperty}} is restricted to have a value from {{list}}, and {{resource}} {{datatypeProperty}} {{value}}, but {{value}} is not in {{list}}, an inconsistency occurs."
    }, #need to come back to this
    Object_All_Values_From = {
        "reference" : "Object All Values From",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?individual rdf:type ?class ; 
        ?objectProperty ?resource .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction;
            owl:onProperty ?objectProperty;
            owl:allValuesFrom ?valueclass ] .''',
        "consequent" : "?resource rdf:type ?valueclass.",
        "explanation" : "Since {{class}} has a restriction on {{objectProperty}} to have all values from {{valueclass}}, {{individual}} rdf:type {{class}}, and {{individual}} {{objectProperty}} {{resource}}, we can infer that {{resource}} rdf:type {{valueclass}}."
    },
    Data_All_Values_From = {
        "reference" : "Data All Values From",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?datatypeProperty ?val .
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?datatypeProperty ;
                owl:allValuesFrom ?value ] .
    FILTER(DATATYPE(?val)!= ?value)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "{{resource}} {{datatypeProperty}} {{val}}, but {{val}} does not have the same datatype {{value}} restricted for {{datatypeProperty}} in {{class}}. Since {{resource}} rdf:type {{class}}, an inconsistency occurs."
    },
    Object_Max_Cardinality = {
        "reference" : "Object Max Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?objectProperty ?object .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:maxCardinality|owl:cardinality ?cardinalityValue ].
    FILTER(?objectCount > ?cardinalityValue)
    {
        SELECT DISTINCT (COUNT(DISTINCT ?object) AS ?objectCount) ?individual ?concept
        WHERE 
        {
            ?individual rdf:type ?concept ;
                ?objectProperty ?object .
            ?objectProperty rdf:type owl:ObjectProperty .
            ?concept rdfs:subClassOf|owl:equivalentClass
                [ rdf:type owl:Restriction ;
                    owl:onProperty ?objectProperty ;
                    owl:maxCardinality|owl:cardinality ?cardinalityValue ].
        } GROUP BY ?individual ?concept
    }
    BIND(?resource AS ?individual)
    BIND(?class AS ?concept)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{objectProperty}} is assigned a maximum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
    },# Still need to check distinctness of object
    Object_Min_Cardinality = {#Works, but for lists of size greater than 1, additional (unnecessary) blank nodes are added. LIMIT 1 on the result would address this, but it is outside the where query
        "reference" : "Object Min Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?objectProperty ?object .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:minCardinality|owl:cardinality ?cardinalityValue ].
    FILTER(?objectCount < ?cardinalityValue)
    {
        SELECT DISTINCT (COUNT(DISTINCT ?object) AS ?objectCount)
        WHERE 
        {
            ?resource rdf:type ?class ;
                ?objectProperty ?object .
            ?objectProperty rdf:type owl:ObjectProperty .
            ?class rdfs:subClassOf|owl:equivalentClass
                [ rdf:type owl:Restriction ;
                    owl:onProperty ?objectProperty ;
                    owl:minCardinality|owl:cardinality ?cardinalityValue ].
        }
    }''',
        "consequent" : "?resource ?objectProperty [ rdf:type owl:Individual ] .",
        "explanation" : "Since {{objectProperty}} is assigned a minimum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is less than {{cardinalityValue}}, we can conclude the existence of additional assignments of {{objectProperty}} for {{resource}}."
    },# Still need to check distinctness
#        Object_Exact_Cardinality_(Max) = {
#            "reference" : "Object Exact Cardinality (Max)",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            "antecedent" :  '''
#    ?resource rdf:type ?class ;
#        ?objectProperty ?object .
#    ?objectProperty rdf:type owl:ObjectProperty .
#    ?class rdfs:subClassOf|owl:equivalentClass
#        [ rdf:type owl:Restriction ;
#            owl:onProperty ?objectProperty ;
#            owl:cardinality ?cardinalityValue ].
#    {
#        SELECT DISTINCT (COUNT(DISTINCT ?object) AS ?objectCount)
#        WHERE 
#        {
#            ?individual rdf:type ?class ;
#                ?objectProperty ?object .
#            ?objectProperty rdf:type owl:ObjectProperty .
#            ?class rdfs:subClassOf|owl:equivalentClass
#                [ rdf:type owl:Restriction ;
#                    owl:onProperty ?objectProperty ;
#                    owl:cardinality ?cardinalityValue ].
#        } GROUP BY ?individual
#    }
#    FILTER(?objectCount > ?cardinalityValue)
#    BIND(?resource AS ?individual)''',
#            "consequent" : "?resource rdf:type owl:Nothing .",
#            "explanation" : "Since {{objectProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
#        },# Still need to check distinctness of object
#        Object_Exact_Cardinality_(Min) = {#Works, but for lists of size greater than 1, additional (unnecessary) blank nodes are added. LIMIT 1 on the result would address this, but it is outside the where query
#            "reference" : "Object Exact Cardinality (Min)",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            "antecedent" :  '''
#    ?resource rdf:type ?class ;
#        ?objectProperty ?object .
#    ?objectProperty rdf:type owl:ObjectProperty .
#    ?class rdfs:subClassOf|owl:equivalentClass
#        [ rdf:type owl:Restriction ;
#            owl:onProperty ?objectProperty ;
#            owl:cardinality ?cardinalityValue ].
#    FILTER(?objectCount < ?cardinalityValue)
#    BIND(?resource AS ?individual)
#    {
#        SELECT DISTINCT (COUNT(DISTINCT ?object) AS ?objectCount) ?individual
#        WHERE 
#        {
#            ?resource rdf:type ?class ;
#                ?objectProperty ?object .
#            ?objectProperty rdf:type owl:ObjectProperty .
#            ?class rdfs:subClassOf|owl:equivalentClass
#                [ rdf:type owl:Restriction ;
#                    owl:onProperty ?objectProperty ;
#                    owl:cardinality ?cardinalityValue ].
#        } GROUP BY ?individual
#    }''',
#            "consequent" : "?resource ?objectProperty [ rdf:type owl:Individual ] .",
#            "explanation" : "Since {{objectProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is less than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
#        },# Still need to check distinctness of object
    Data_Max_Cardinality = {
        "reference" : "Data Max Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?dataProperty ?data .
    ?dataProperty rdf:type owl:DatatypeProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?dataProperty ;
            owl:maxCardinality ?cardinalityValue ] .
    {
        SELECT DISTINCT (COUNT(DISTINCT ?data) AS ?dataCount)
        WHERE 
        {
            ?resource rdf:type ?class ;
                ?dataProperty ?data .
            ?dataProperty rdf:type owl:DatatypeProperty .
            ?class rdfs:subClassOf|owl:equivalentClass
                [ rdf:type owl:Restriction ;
                    owl:onProperty ?dataProperty ;
                    owl:maxCardinality ?cardinalityValue ].
        }
    }
    FILTER(?dataCount > ?cardinalityValue)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{dataProperty}} is assigned a maximum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
    },
    Data_Min_Cardinality = {
        "reference" : "Data Min Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?dataProperty ?data .
    ?dataProperty rdf:type owl:DatatypeProperty .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?dataProperty ;
                owl:minCardinality ?cardinalityValue ] .
    {
        SELECT DISTINCT (COUNT(DISTINCT ?data) AS ?dataCount)
        WHERE 
        {
            ?resource rdf:type ?class ;
                ?dataProperty ?data .
            ?dataProperty rdf:type owl:DatatypeProperty .
            ?class rdf:type owl:Class ;
                rdfs:subClassOf|owl:equivalentClass
                    [ rdf:type owl:Restriction ;
                        owl:onProperty ?dataProperty ;
                        owl:minCardinality ?cardinalityValue ].
        }
    }
    FILTER(?dataCount < ?cardinalityValue)''',
        "consequent" : "?resource ?dataProperty [ rdf:type rdfs:Datatype ] .",
        "explanation" : "Since {{dataProperty}} is assigned a minimum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is less than {{cardinalityValue}}, we can conclude the existence of additional assignments of {{dataProperty}} for {{resource}}."
    },
    Data_Exact_Cardinality = {
        "reference" : "Data Exact Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?dataProperty ?data .
    ?dataProperty rdf:type owl:DatatypeProperty .
    ?class rdf:type owl:Class ; 
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?dataProperty ;
                owl:cardinality ?cardinalityValue ] .
    {
        SELECT DISTINCT (COUNT(DISTINCT ?data) AS ?dataCount)
        WHERE 
        {
            ?resource rdf:type ?class ;
                ?dataProperty ?data .
            ?dataProperty rdf:type owl:DatatypeProperty .
            ?class rdf:type owl:Class ;
                rdfs:subClassOf|owl:equivalentClass
                    [ rdf:type owl:Restriction ;
                        owl:onProperty ?dataProperty ;
                        owl:cardinality ?cardinalityValue ].
        }
    }
    FILTER(?dataCount > ?cardinalityValue)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{dataProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
    }, # -- This is currently only accounting for max. Min accounted for in data min rule
    Object_Union_Of = {
        "reference" : "Object Union Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Class ;
                owl:unionOf ?list ] .
    ?list rdf:rest*/rdf:first ?member .''',
        "consequent" : "?member rdfs:subClassOf ?resource .",
        "explanation" : "Since the class {{resource}} has a subclass or equivalent class relation with a class that comprises the union of {{list}}, which contains member {{member}}, we can infer that {{member}} is a subclass of {{resource}}."
    },
    Disjoint_Union = {
        "reference" : "Disjoint Union",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Class ;
                owl:disjointUnionOf ?list ] .
    ?list rdf:rest*/rdf:first ?member .
    {
        SELECT DISTINCT ?item ?class WHERE 
        {
            ?class rdf:type owl:Class ;
                rdfs:subClassOf|owl:equivalentClass
                    [ rdf:type owl:Class ;
                        owl:disjointUnionOf ?list ] .
            ?list rdf:rest*/rdf:first ?item .
        }
    }
    FILTER(?resource = ?class)
    FILTER(?member != ?item)''',
        "consequent" : "?member rdfs:subClassOf ?resource ; owl:disjointWith ?item .",
        "explanation" : "Since the class {{resource}} has a subclass or equivalent class relation with a class that comprises the disjoint union of {{list}}, which contains member {{member}}, we can infer that {{member}} is a subclass of {{resource}} and disjoint with the other members of the list."
    },
    Data_Union_Of = {
        "reference" : "Data Union Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Class ;
                owl:unionOf ?list ] .
    ?list rdf:rest*/rdf:first ?member .
    ?member rdf:type owl:Restriction ;
        owl:onProperty ?dataProperty ;
        owl:someValuesFrom ?datatype . 
    ?dataProperty rdf:type owl:DatatypeProperty .
    ?resource ?dataProperty ?data .
    FILTER(DATATYPE(?data)=?datatype)''', #need to come back and make sure logic is correct on this one
        "consequent" : "?resource rdf:type ?class .",
        "explanation" : ""#add explanation here
    },
    Object_Complement_Of = {
        "reference" : "Object Complement Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ,
            ?complementClass .
    ?class rdf:type owl:Class .
    ?complementClass rdf:type owl:Class .
    {?class owl:complementOf ?complementClass .} 
        UNION 
    {?complementClass owl:complementOf ?class .}''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{class}} and {{complementClass}} are complementary, {{resource}} being of type both {{class}} and {{complementClass}} leads to an inconsistency."
    },
    Data_Complement_Of = {
        "reference" : "Data Complement Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?datatype rdf:type rdfs:Datatype ;
        owl:datatypeComplementOf ?complement .
    ?resource ?dataProperty ?value .
    ?dataProperty rdf:type owl:DatatypeProperty ;
        rdfs:range ?datatype .
    FILTER(DATATYPE(?value) = ?complement)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{datatype}} is the complement of {{complement}}, {{dataProperty}} has range {{datatype}}, and {{resource}} {{dataProperty}} {{value}}, but {{value}} is of type {{complement}}, an inconsistency occurs."
    },
    Object_Property_Complement_Of = {
        "reference" : "Object Property Complement Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Class ;
                owl:complementOf 
                    [ rdf:type owl:Restriction ;
                        owl:onProperty ?objectProperty ;
                        owl:someValuesFrom ?restrictedClass ] 
            ] .
    ?resource rdf:type ?class ;
        ?objectProperty [ rdf:type ?objectClass ] .
    ?objectProperty rdf:type owl:ObjectProperty .
    {
        FILTER(?objectClass = ?restrictedClass)
    }
    UNION
    {
        ?objectClass rdfs:subClassOf*|owl:equivalentClass ?restrictedClass . 
    }''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{class}} is a subclass of or is equivalent to a class with a complement restriction on the use of {{objectProperty}} to have values from {{restrictedClass}}, and {{resource}} is of type {{class}}, but has the link {{objectProperty}} to have values from an instance of {{restrictedClass}}, an inconsistency occurs." # do we also consider lists or complementary properties here?
    },
    Data_Property_Complement_Of = {
        "reference" : "Data Property Complement Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Class ;
                owl:complementOf 
                    [ rdf:type owl:Restriction ;
                        owl:onProperty ?dataProperty ;
                        owl:someValuesFrom ?datatype ] 
            ] .
    ?resource rdf:type ?class ;
        ?dataProperty ?value .
    ?dataProperty rdf:type owl:DatatypeProperty .
    FILTER(DATATYPE(?value)=?datatype)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{resource}} is a {{class}} which is equivalent to or a subclass of a class that has a complement of restriction on {{dataProperty}} to have some values from {{datatype}}, {{resource}} {{dataProperty}} {{value}}, but {{value}} has a datatype {{datatype}}, an inconsistency occurs."
    },
    Object_Intersection_Of = {
        "reference" : "Object Intersection Of",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?class rdf:type owl:Class ;
        owl:intersectionOf ?list .
    ?list rdf:rest*/rdf:first ?member .
    {
        ?member rdf:type owl:Class .
        ?resource rdf:type ?member .
    }
    UNION 
    {
        ?member rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:someValuesFrom ?restrictedClass .
        ?objectProperty rdf:type owl:ObjectProperty .
        ?resource ?objectProperty [rdf:type  ?restrictedClass ] .
    }
    {
        SELECT DISTINCT * WHERE
        {
            ?concept rdf:type owl:Class ;
                owl:intersectionOf ?list .
            ?list rdf:rest*/rdf:first ?item .
            {
                ?item rdf:type owl:Class .
                ?individual rdf:type ?item .
            }
            UNION
            {
                ?item rdf:type owl:Restriction ;
                    owl:onProperty ?objectProperty ;
                    owl:someValuesFrom ?restrictedClass .
                ?objectProperty rdf:type owl:ObjectProperty .
                ?individual ?objectProperty [rdf:type  ?restrictedClass ] .
            }
        }
    }
    BIND(?class AS ?concept) 
    BIND(?resource AS ?individual) 
    FILTER(?member != ?item)
    ''',# As currently implemented, i think that is the resource is of type any two members in the list, it gets assigned to be of type class
        "consequent" : "?resource rdf:type ?class.",
        "explanation" : "Since {{class}} is the intersection of the the members in {{list}}, and {{resource}} is of type each of the members in the list, then we can infer {{resource}} is a {{class}}."
    },
#        Data_Intersection_Of = {
#            "reference" : "Data Intersection Of",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            "antecedent" :  '''
#    ?datatype rdf:type rdfs:Datatype ;
#        owl:intersectionOf ?list .
#    ?list rdf:rest*/rdf:first ?member .''',
#            "consequent" : "?resource rdf:type owl:Nothing .",
#            "explanation" : ""
#        },
    Object_Qualified_Max_Cardinality = {
        "reference" : "Object Qualified Max Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?objectProperty ?object .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?object rdf:type ?restrictedClass .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:onClass ?restrictedClass ;
            owl:maxQualifiedCardinality|owl:qualifiedCardinality ?cardinalityValue ].
    FILTER(?objectCount > ?cardinalityValue)
    {
        SELECT DISTINCT (COUNT(DISTINCT ?object) AS ?objectCount) ?individual ?concept
        WHERE 
        {
            ?individual rdf:type ?concept ;
                ?objectProperty ?object .
            ?object rdf:type ?restrictedClass .
            ?objectProperty rdf:type owl:ObjectProperty .
            ?concept rdfs:subClassOf|owl:equivalentClass
                [ rdf:type owl:Restriction ;
                    owl:onProperty ?objectProperty ;
                    owl:onClass ?restrictedClass ;
                    owl:maxQualifiedCardinality|owl:qualifiedCardinality ?cardinalityValue ].
        } GROUP BY ?individual ?concept
    }
    BIND(?resource AS ?individual)
    BIND(?class AS ?concept)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{class}} is constrained with a qualified max cardinality restriction on property {{objectProperty}} to have a max of {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}} which is more than {{value}}, we can infer that an inconsistency occurs."
    },
    Object_Qualified_Min_Cardinality = {
        "reference" : "Object Qualified Min Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?objectProperty ?object .
    ?object rdf:type ?restrictedClass .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ; 
            owl:minQualifiedCardinality|owl:qualifiedCardinality ?value ;
            owl:onClass ?restrictedClass ] .
    {
        SELECT (COUNT(DISTINCT ?object) AS ?objectCount) ?individual ?concept WHERE 
        {          
            ?individual rdf:type ?concept ;
                ?objectProperty ?object .
            ?object rdf:type ?restrictedClass .
            ?objectProperty rdf:type owl:ObjectProperty .
            ?concept rdfs:subClassOf|owl:equivalentClass
                [ rdf:type owl:Restriction ;
                    owl:onProperty ?objectProperty ; 
                    owl:minQualifiedCardinality|owl:qualifiedCardinality ?value ;
                    owl:onClass ?restrictedClass ] .
        } GROUP BY ?individual ?concept
    }
    BIND(?resource AS ?individual)
    BIND(?class AS ?concept)
    FILTER(?objectCount < ?value)''',
        "consequent" : "?resource ?objectProperty [ rdf:type owl:Individual ] .",
        "explanation" : "Since {{class}} is constrained with a qualified min cardinality restriction on property {{objectProperty}} to have a min of {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}} which is less than {{value}}, we can infer the existence of another object."
    },
#        Object_Qualified_Exact_Cardinality_(Max) = { # incorporated into object qualified min and max
#            "reference" : "Object Qualified Exact Cardinality (Max)",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            "antecedent" :  '''
#    ?resource rdf:type ?class ;
#        ?objectProperty ?object .
#    ?objectProperty rdf:type owl:ObjectProperty .
#    ?object rdf:type ?restrictedClass .
#    ?class rdfs:subClassOf|owl:equivalentClass
#        [ rdf:type owl:Restriction ;
#            owl:onProperty ?objectProperty ;
#            owl:onClass ?restrictedClass ;
#            owl:qualifiedCardinality ?cardinalityValue ].
#    {
#        SELECT DISTINCT (COUNT(DISTINCT ?object) AS ?objectCount) ?individual ?concept
#        WHERE 
#        {
#            ?individual rdf:type ?concept ;
#                ?objectProperty ?object .
#            ?object rdf:type ?restrictedClass .
#            ?objectProperty rdf:type owl:ObjectProperty .
#            ?concept rdfs:subClassOf|owl:equivalentClass
#                [ rdf:type owl:Restriction ;
#                    owl:onProperty ?objectProperty ;
#                    owl:onClass ?restrictedClass ;
#                    owl:qualifiedCardinality ?cardinalityValue ].
#        } GROUP BY ?individual ?concept
#    }
#    BIND(?resource AS ?individual)
#    BIND(?class AS ?concept)
#    FILTER(?objectCount > ?cardinalityValue)''',
#            "consequent" : "?resource rdf:type owl:Nothing .",
#            "explanation" : "Since {{class}} is constrained with a qualified cardinality restriction on property {{objectProperty}} to have {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}}, an inconsistency occurs."
#        },
#        Object_Qualified_Exact_Cardinality_(Min) = {
#            "reference" : "Object Qualified Exact Cardinality (Min)",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            "antecedent" :  '''
#    ?resource rdf:type ?class ;
#        ?objectProperty ?object .
#    ?object rdf:type ?restrictedClass .
#    ?objectProperty rdf:type owl:ObjectProperty .
#    ?class rdfs:subClassOf|owl:equivalentClass
#        [ rdf:type owl:Restriction ;
#            owl:onProperty ?objectProperty ; 
#            owl:qualifiedCardinality ?value ;
#            owl:onClass ?restrictedClass ] .
#    {
#      SELECT (COUNT(DISTINCT ?object) AS ?objectCount) ?individual ?concept WHERE 
#        {          
#            ?individual rdf:type ?concept ;
#                ?objectProperty ?object .
#            ?object rdf:type ?restrictedClass .
#            ?objectProperty rdf:type owl:ObjectProperty .
#            ?concept rdfs:subClassOf|owl:equivalentClass
#                [ rdf:type owl:Restriction ;
#                    owl:onProperty ?objectProperty ; 
#                    owl:owl:qualifiedCardinality ?value ;
#                    owl:onClass ?restrictedClass ] .
#        } GROUP BY ?individual
#    }
#    BIND(?resource AS ?individual)
#    BIND(?class AS ?concept)
#    FILTER(?objectCount < ?value)''',
#            "consequent" : "?resource ?objectProperty [ rdf:type owl:Individual ] .",
#            "explanation" : "Since {{class}} is constrained with a qualified cardinality restriction on property {{objectProperty}} to have {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}} which is less than {{value}}, we can infer the existence of another object."
#        },
    Data_Qualified_Max_Cardinality = {
        "reference" : "Data Qualified Max Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?datatypeProperty ?value .
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?restriction rdf:type owl:Restriction ;
        owl:onProperty ?datatypeProperty ;
        owl:maxQualifiedCardinality ?cardinalityValue ;
        owl:onDataRange ?datatype .
    {
        SELECT (COUNT(DISTINCT ?value) AS ?valueCount) ?individual WHERE
        {
            ?individual ?datatypeProperty ?value .
            ?datatypeProperty rdf:type owl:DatatypeProperty .
            ?restriction rdf:type owl:Restriction ;
                owl:onProperty ?datatypeProperty ;
                owl:maxQualifiedCardinality ?cardinalityValue ;
                owl:onDataRange ?datatype .
        } GROUP BY ?individual
    }
    BIND(?resource AS ?individual)
    FILTER(DATATYPE(?value) = ?datatype)
    FILTER(?valueCount > ?cardinalityValue)''',
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{datatypeProperty}} is constrained with a qualified max cardinality restriction on datatype {{datatype}} to have a max of {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, an inconsistency occurs."
    },
    Data_Qualified_Min_Cardinality = {
        "reference" : "Data Qualified Min Cardinality",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource ?datatypeProperty ?value .
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?restriction rdf:type owl:Restriction ;
        owl:onProperty ?datatypeProperty ;
        owl:minQualifiedCardinality ?cardinalityValue ;
        owl:onDataRange ?datatype .
    {
        SELECT (COUNT(DISTINCT ?value) AS ?valueCount) ?individual WHERE
        {
            ?individual ?datatypeProperty ?value .
            ?datatypeProperty rdf:type owl:DatatypeProperty .
            ?restriction rdf:type owl:Restriction ;
                owl:onProperty ?datatypeProperty ;
                owl:minQualifiedCardinality ?cardinalityValue ;
                owl:onDataRange ?datatype .
        } GROUP BY ?individual
    }
    BIND(?resource AS ?individual)
    FILTER(DATATYPE(?value) = ?datatype)
    FILTER(?valueCount < ?cardinalityValue)''',
        "consequent" : "?resource ?datatypeProperty [ rdf:type rdfs:Datatype ] .",
        "explanation" : "Since {{datatypeProperty}} is constrained with a qualified min cardinality restriction on datatype {{datatype}} to have a min of {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, we can infer the existence of at least one more additional value."
    },
#        Data_Qualified_Exact_Cardinality = {#result shows up in blazegraph, but triple is not being added
#            "reference" : "Data Qualified Exact Cardinality",
#            "resource" : "?resource", 
#            "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            "antecedent" :  '''
#    ?resource ?datatypeProperty ?value .
#    ?datatypeProperty rdf:type owl:DatatypeProperty .
#    ?restriction rdf:type owl:Restriction ;
#        owl:onProperty ?datatypeProperty ;
##        owl:onDataRange ?datatype ;
#        owl:qualifiedCardinality ?cardinalityValue .
#    {
#        SELECT (COUNT(DISTINCT ?value) AS ?valueCount) ?individual WHERE
#        {
#            ?resource ?datatypeProperty ?value .
#            ?datatypeProperty rdf:type owl:DatatypeProperty .
#            ?restriction rdf:type owl:Restriction ;
#                owl:onProperty ?datatypeProperty ;
##                owl:onDataRange ?datatype ;
#                owl:qualifiedCardinality ?cardinalityValue .
#        } GROUP BY ?individual
#    }
#    BIND(?resource AS ?individual)
##    FILTER(DATATYPE(?value) = ?datatype)
#    FILTER(?valueCount > ?cardinalityValue)''',
#            "consequent" : "?resource rdf:type owl:Nothing .",
#            "explanation" : "Since {{datatypeProperty}} is constrained with a qualified cardinality restriction on datatype {{datatype}} to have {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, an inconsistency occurs."# currently the same as qualified max. need to incorporate min requirement
#        },
    Datatype_Restriction = {
        "reference" : "Datatype Restriction",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?resource rdf:type ?class ;
        ?dataProperty ?value .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?dataProperty ; 
                owl:someValuesFrom ?datatype ] .
    ?dataProperty rdf:type owl:DatatypeProperty .
    ?datatype rdf:type rdfs:Datatype ;
        owl:onDatatype ?restrictedDatatype ;
        owl:withRestrictions ?list .
    {
        ?list rdf:first ?min .
        ?list rdf:rest/rdf:first ?max .
        ?min xsd:minInclusive ?minValue .
        ?max xsd:maxInclusive ?maxValue .
    }
    UNION
    {
        ?list rdf:first ?max .
        ?list rdf:rest/rdf:first ?min .
        ?min xsd:minInclusive ?minValue .
        ?max xsd:maxInclusive ?maxValue .
    }
    FILTER(?value < ?minValue || ?value > ?maxValue)''',# assuming with restriction of the form min exclusive max exclusive
        "consequent" : "?resource rdf:type owl:Nothing .",
        "explanation" : "Since {{class}} has a with restriction on datatype property {{dataProperty}} to be within the range specified in {{list}} with min value {{minValue}} and max value {{maxValue}}, and {{resource}} is of type {{class}} and has a value {{value}} for {{dataProperty}} which is outside the specified range, an inconsistency occurs."
    },
    All_Disjoint_Classes = {
        "reference" : "All Disjoint Classes",
        "resource" : "?restriction", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?restriction rdf:type owl:AllDisjointClasses ;
        owl:members ?list .
    ?list rdf:rest*/rdf:first ?member .
    {
        SELECT DISTINCT ?item ?restrict WHERE
        {
            ?restrict rdf:type owl:AllDisjointClasses ;
                owl:members ?list .
            ?list rdf:rest*/rdf:first ?item .
        }
    }
    BIND(?restriction AS ?restrict)
    FILTER(?member != ?item)''', 
        "consequent" : "?member owl:disjointWith ?item .",
        "explanation" : "Since {{restriction}} is an all disjoint classes restriction with classes listed in {{list}}, each member in {{list}} is disjoint with each other member in the list."
    },
    All_Disjoint_Properties = {
        "reference" : "All Disjoint Properties",
        "resource" : "?restriction", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?restriction rdf:type owl:AllDisjointProperties ;
        owl:members ?list .
    ?list rdf:rest*/rdf:first ?member .
    {
        SELECT DISTINCT ?item ?restrict WHERE
        {
            ?restrict rdf:type owl:AllDisjointProperties ;
                owl:members ?list .
            ?list rdf:rest*/rdf:first ?item .
        }
    }
    BIND(?restriction AS ?restrict) 
    FILTER(?member != ?item)''',
        "consequent" : "?member owl:propertyDisjointWith ?item .",
        "explanation" : "Since {{restriction}} is an all disjoint properties restriction with properties listed in {{list}}, each member in {{list}} is disjoint with each other property in the list."
    },
    Object_Property_Chain_Inclusion = {
        "reference" : "Object Property Chain Inclusion",
        "resource" : "?resource", 
        "prefixes" : {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        "antecedent" :  '''
    ?objectProperty rdf:type owl:ObjectProperty ;
        owl:propertyChainAxiom ?list .
    ?list rdf:first ?prop1 .
    ?list rdf:rest/rdf:first ?prop2 .
    ?resource ?prop1 [ ?prop2 ?o ] .''',
        "consequent" : "?resource ?objectProperty ?o .",
        "explanation" : ""#currently limited to two properties
    }
)

# base config class; extend it to your needs.
Config = dict(
    # use DEBUG mode?
    DEBUG = False,

    site_name = "Whyis Knowledge Graph",

    base_rate_probability = 0.6,

    # use TESTING mode?
    TESTING = False,

    #JS CONFIG - VUE JS
    ##USE CUSTOM REST BACKUP & RESTORE
    THIRD_PARTY_REST_BACKUP = True,
    DISABLE_VUE_SPEED_DIAL = True,

    # use server x-sendfile?
    USE_X_SENDFILE = False,

    WTF_CSRF_ENABLED = True,
    SECRET_KEY = "secret",  # import os; os.urandom(24)

    site_url_path = '/',

    nanopub_archive = {
        'depot.storage_path' : "/data/nanopublications",
    },
    delete_archive_nanopubs = False,

    file_archive = {
        'cache_max_age' : 3600*24*7,
        'depot.storage_path' : '/data/files'
    },
    vocab_file = "default_vocab.ttl",
    WHYIS_TEMPLATE_DIR = None,
    WHYIS_CDN_DIR = None,

    DEFAULT_ANONYMOUS_READ = False,

    site_header_image = '/static/images/random_network.png',

    # JAVA
    JAVA_CLASSPATH = '/apps/whyis/jars',

    # LOGGING
    LOGGER_NAME = "%s_log" % project_name,
    LOG_FILENAME = "/var/log/%s/output-%s.log" % (project_name,str(datetime.now()).replace(' ','_')),
    LOG_LEVEL = logging.INFO,
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s", # used by logging.Formatter

    PERMANENT_SESSION_LIFETIME = timedelta(days=7),

    # EMAIL CONFIGURATION
    ## MAIL_SERVER = "smtp.mailgun.org",
    ## MAIL_PORT = 587,
    ## MAIL_USE_TLS = True,
    ## MAIL_USE_SSL = False,
    ## MAIL_DEBUG = False,
    ## MAIL_USERNAME = '',
    ## MAIL_PASSWORD = '',
    ## DEFAULT_MAIL_SENDER = "Whyis Admin <admin@whyis.example.com>",

    # see example/ for reference
    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = [],

    lod_prefix = LOD_PREFIX,
    SECURITY_EMAIL_SENDER = "Name <email@example.com>",
    SECURITY_FLASH_MESSAGES = True,
    SECURITY_CONFIRMABLE = False,
    SECURITY_CHANGEABLE = True,
    SECURITY_TRACKABLE = True,
    SECURITY_RECOVERABLE = True,
    SECURITY_REGISTERABLE = True,
    SECURITY_PASSWORD_HASH = 'sha512_crypt',
    SECURITY_PASSWORD_SALT = 'changeme__',
    SECURITY_SEND_REGISTER_EMAIL = False,
    SECURITY_POST_LOGIN_VIEW = "/",
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False,
    SECURITY_DEFAULT_REMEMBER_ME = True,
    ADMIN_EMAIL_RECIPIENTS = [],
    db_defaultGraph = LOD_PREFIX + '/',

    java_classpath = "/apps/whyis/jars",

    admin_queryEndpoint = 'http://localhost:8080/blazegraph/namespace/admin/sparql',
    admin_updateEndpoint = 'http://localhost:8080/blazegraph/namespace/admin/sparql',

    knowledge_queryEndpoint = 'http://localhost:8080/blazegraph/namespace/knowledge/sparql',
    knowledge_updateEndpoint = 'http://localhost:8080/blazegraph/namespace/knowledge/sparql',

    LOGIN_USER_TEMPLATE = "auth/login.html",
    CELERY_BROKER_URL = 'redis://localhost:6379/0',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0',

    CACHE_TYPE = "simple", # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 0,

    namespaces = [
        importer.LinkedData(
            prefix = LOD_PREFIX+'/doi/',
            url = 'http://dx.doi.org/%s',
            headers={'Accept':'text/turtle'},
            format='turtle',
            postprocess_update= ['''insert {
                graph ?g {
                    ?pub a <http://purl.org/ontology/bibo/AcademicArticle>.
                }
            } where {
                graph ?g {
                    ?pub <http://purl.org/ontology/bibo/doi> ?doi.
                }
            }''',
            '''delete {
              ?author <http://www.w3.org/2002/07/owl#sameAs> ?orcid.
            } insert {
                graph ?g {
                    ?author <http://www.w3.org/ns/prov#specializationOf> ?orcid.
                }
            } where {
                graph ?g {
                    ?author a <http://xmlns.com/foaf/0.1/Person>;
                      <http://www.w3.org/2002/07/owl#sameAs> ?orcid.
                }
            }
            ''']
        ),
        importer.LinkedData(
            prefix = LOD_PREFIX+'/orcid/',
            url = 'http://orcid.org/%s',
            headers={'Accept':'application/ld+json'},
            format='json-ld',
            replace=[
                ('\\"http:\\/\\/schema\\.org\\",', '{"@vocab" : "http://schema.org/"},'),
                ('https://doi.org/', 'http://dx.doi.org/'),
                ('https://', 'http://'),
            ],
            postprocess_update= ['''delete {
              ?org ?p ?o.
              ?s ?p ?org.
            } insert {
                graph ?g {
                    ?s ?p ?o.
                }
            } where {
                graph ?g {
                    {
                    ?org a <http://schema.org/Organization>;
                      <http://schema.org/identifier> [
                          a <http://schema.org/PropertyValue>;
                          <http://schema.org/propertyID> ?propertyID;
                          <http://schema.org/value> ?idValue;
                      ].
                      ?org ?p ?o.
                      bind(IRI(concat("%s/organization/", str(?propertyID),"/",str(?idValue))) as ?s)
                    } union {
                    ?org a <http://schema.org/Organization>;
                      <http://schema.org/identifier> [
                          a <http://schema.org/PropertyValue>;
                          <http://schema.org/propertyID> ?propertyID;
                          <http://schema.org/value> ?idValue;
                      ].
                      ?s ?p ?org.
                      bind(IRI(concat("%s/organization/", str(?propertyID),"/",str(?idValue))) as ?o)
                    }
                }
            }'''  % (LOD_PREFIX, LOD_PREFIX) ,
            '''
            insert {
                graph ?g {
                    ?s <http://schema.org/name> ?name.
                }
            } where {
                graph ?g {
                    ?s <http://schema.org/alternateName> ?name.
                }
            }
            ''']
        ),
        importer.LinkedData(
            prefix = LOD_PREFIX+'/dbpedia/',
            url = 'http://dbpedia.org/resource/%s',
            headers={'Accept':'text/turtle'},
            format='turtle',
            postprocess_update= '''insert {
                graph ?g {
                    ?article <http://purl.org/dc/terms/abstract> ?abstract.
                }
            } where {
                graph ?g {
                    ?article <http://dbpedia.org/ontology/abstract> ?abstract.
                }
            }
            '''
        ),
        importer.LinkedData(
            prefix = LOD_PREFIX+'/dbpedia/ontolgy/',
            url = 'http://dbpedia.org/ontology/%s',
            headers={'Accept':'text/turtle'},
            format='turtle',
        ),
#        importer.LinkedData(
#            prefix = LOD_PREFIX+'/dbpedia/class/',
#            url = 'http://dbpedia.org/class/%s',
#            access_url = 'http://dbpedia.org/sparql?default-graph-uri=http://dbpedia.org&query=DESCRIBE+<%s>&format=application/json-ld',
#            format='json-ld',
#        )
    ],
    active_profiles = ["Inheritance"],
    reasoning_profiles = {
        "Inheritance" : ["Class Inclusion", "Individual Inclusion", "Object Property Inclusion", "Data Property Inclusion"],
        "OWL2 EL" : [
            "Class Inclusion",
            "Class Equivalence",
            "Class Disjointness",
            "Property Inclusion",
            "Object Property Inclusion",
            "Data Property Inclusion",
            "Property Equivalence",
            "Object Property Transitivity",
            "Object Property Reflexivity",
            "Property Domain",
            "Property Range",
            "Functional Data Property",
            #"Assertions", (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
            "Same Individual",
            "Different Individuals",
            "Class Assertion",
            #"Positive Object Property Assertion",
            #"Positive Data Property Assertion",
            "Negative Object Property Assertion",
            "Negative Data Property Assertion",
            "Keys",
            #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom)
            "Object Some Values From",
            "Data Some Values From",
            #"Individual Existential Quantification" (ObjectHasValue, DataHasValue)
            "Object Has Value",
            "Data Has Value",
            #"Self Restriction" (ObjectHasSelf)
            "Object Has Self",
            #"Individual Enumeration" (ObjectOneOf, DataOneOf) # need to traverse lists to do
            #"Object One Of",
            #"Data One Of",
            #"Intersection" (ObjectIntersectionOf, DataIntersectionOf)
            #"Object Intersection Of",
            #"Data Intersection Of",
        ],
        "OWL2 QL" : [
            "Class Inclusion",
            "Class Equivalence",
            "Class Disjointness",
            "Object Property Inversion",
            "Property Inclusion",
            "Property Domain",
            "Property Range",
            "Property Disjointness",
            "Object Property Symmetry",
            "Object Property Reflexivity",
            "Object Property Irreflexivity",
            "Object Property Asymmetry",
            #"Assertions", (DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, and DataPropertyAssertion)
            "Different Individuals",
            "Class Assertion",
            #"Positive Object Property Assertion",
            #"Positive Data Property Assertion"
            #
            #Negation
            "Object Complement Of",
            "Object Property Complement Of",
            "Data Property Complement Of",
        ],
        "OWL2 RL" : [ # Note that only disjoint union and object property reflexitivity are not supported
            "Class Disjointness",
            "Object Property Transitivity",
            "Property Domain",
            "Property Range",
            "Functional Data Property",
            "Functional Object Property",
            "Object Property Irreflexivity",
            #"Inverse Functional Object Property",
            "Property Disjointness",
            "Object Property Symmetry",
            "Object Property Asymmetry",
            "Class Inclusion",
            "Property Inclusion",
            "Object Property Inclusion",
            "Data Property Inclusion",
            "Class Equivalence",
            "Property Equivalence",
            "Object Property Inversion",
            #"Assertions" (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
            "Same Individual",
            "Different Individuals",
            "Class Assertion",
            #"Positive Object Property Assertion",
            #"Positive Data Property Assertion",
            "Negative Object Property Assertion",
            "Negative Data Property Assertion",
            "Keys",
            #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom)
            "Object Some Values From",
            "Data Some Values From",
            #"Self Restriction" (ObjectHasSelf)
            "Object Has Self",
            #"Individual Existential Quantification" (ObjectHasValue, DataHasValue)
            "Object Has Value",
            "Data Has Value",
            #"Individual Enumeration" (ObjectOneOf, DataOneOf) # need to traverse lists to do
            #"Object One Of",
            #"Data One Of",
            #"Class Universal Quantification" (ObjectAllValuesFrom, DataAllValuesFrom)
            "Object All Values From",
            "Data All Values From",
            #"Cardinality Restriction" (ObjectMaxCardinality, ObjectMinCardinality, ObjectExactCardinality, DataMaxCardinality, DataMinCardinality, DataExactCardinality)
            #"Object Max Cardinality",
            #"Object Min Cardinality",
            #"Object Exact Cardinality",
            #"Object Qualified Max Cardinality",
            #"Object Qualified Min Cardinality",
            #"Object Qualified Exact Cardinality",
            "Data Max Cardinality",
            #"Data Min Cardinality",
            #"Data Exact Cardinality",
            #"Data Qualified Max Cardinality",
            #"Data Qualified Min Cardinality",
            #"Data Qualified Exact Cardinality",
            #"Datatype Restriction"
            # Disjunction  (ObjectUnionOf, and DataUnionOf)
        ], 
        "OWL DL" : [
            "Class Disjointness",
            "Object Property Transitivity",
            "Property Domain",
            "Property Range",
            "Functional Data Property",
            "Functional Object Property",
            "Object Property Irreflexivity",
            "Inverse Functional Object Property",
            "Property Disjointness",
            "Object Property Symmetry",
            "Object Property Asymmetry",
            "Object Property Reflexivity",
            "Class Inclusion",
            "Property Inclusion",
            "Individual Inclusion",
            "Object Property Inclusion",
            "Data Property Inclusion",
            "Class Equivalence",
            "Property Equivalence",
            "Object Property Inversion",
            "Object Complement Of",
            #"Assertions" (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
            "Same Individual",
            "All Different Individuals",
            "All Disjoint Classes",
            "All Disjoint Properties",
            "Data Complement Of",
            "Data Property Complement Of",
            "Different Individuals",
            "Class Assertion",
            #"Positive Object Property Assertion",
            #"Positive Data Property Assertion",
            "Negative Object Property Assertion",
            "Negative Data Property Assertion",
            "Keys",
            #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom)
            "Object Some Values From",
            "Data Some Values From",
            #"Self Restriction" (ObjectHasSelf)
            "Object Has Self",
            #"Individual Existential Quantification" (ObjectHasValue, DataHasValue)
            "Object Has Value",
            "Data Has Value",
            "Object Property Complement Of",
            #"Individual Enumeration" (ObjectOneOf, DataOneOf) # need to traverse lists to do
            "Object One Of Membership",
            "Object One Of Inconsistency",
            "Data One Of",
            #"Class Universal Quantification" (ObjectAllValuesFrom, DataAllValuesFrom)
            "Object All Values From",
            "Data All Values From",
            #"Cardinality Restriction" (ObjectMaxCardinality, ObjectMinCardinality, ObjectExactCardinality, DataMaxCardinality, DataMinCardinality, DataExactCardinality)
            "Object Max Cardinality",
            "Object Min Cardinality",
            "Object Exact Cardinality",
            "Object Qualified Max Cardinality",
            "Object Qualified Min Cardinality",
            "Object Qualified Exact Cardinality",
            "Data Max Cardinality",
            "Data Min Cardinality",
            "Data Exact Cardinality",
            "Data Qualified Max Cardinality",
            "Data Qualified Min Cardinality",
            "Data Qualified Exact Cardinality",
            "Datatype Restriction",
            # Disjunction  (ObjectUnionOf, and DataUnionOf)
            "Data Union Of",
            "Disjoint Union",
            "Object Union Of",
            "Object Property Chain Inclusion",
            "Object Intersection Of",
            "Data Intersection Of"
        ]  ,  # "All Different Individuals" -> differentFrom individuals. AllDisjointClasses --> pairwise disjoint classes . Also need minInclusive, maxInclusive, (DisjointUnion not supported in RL), ObjectPropertyChainInclusion
        "OWL DL Back Tracer" : [
            "Class Disjointness Back Tracer"
        ]
    },
    inferencers  = {
        "Class Disjointness" : autonomic.Deductor(
            reference =  InferenceRules["Class_Disjointness"]["reference"],
            resource = InferenceRules["Class_Disjointness"]["resource"] , 
            prefixes = InferenceRules["Class_Disjointness"]["prefixes"] , 
            antecedent =  InferenceRules["Class_Disjointness"]["antecedent"] ,
            consequent = InferenceRules["Class_Disjointness"]["consequent"] ,
            explanation = InferenceRules["Class_Disjointness"]["explanation"]
        ),
        "Object Property Transitivity" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Transitivity"]["reference"],
            resource = InferenceRules["Object_Property_Transitivity"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Transitivity"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Transitivity"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Transitivity"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Transitivity"]["explanation"]
        ),
        "Object Property Reflexivity" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Reflexivity"]["reference"],
            resource = InferenceRules["Object_Property_Reflexivity"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Reflexivity"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Reflexivity"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Reflexivity"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Reflexivity"]["explanation"]
        ),
        "Property Domain" : autonomic.Deductor(
            reference =  InferenceRules["Property_Domain"]["reference"],
            resource = InferenceRules["Property_Domain"]["resource"] , 
            prefixes = InferenceRules["Property_Domain"]["prefixes"] , 
            antecedent =  InferenceRules["Property_Domain"]["antecedent"] ,
            consequent = InferenceRules["Property_Domain"]["consequent"] ,
            explanation = InferenceRules["Property_Domain"]["explanation"]
        ),
        "Property Range" : autonomic.Deductor(
            reference =  InferenceRules["Property_Range"]["reference"],
            resource = InferenceRules["Property_Range"]["resource"] , 
            prefixes = InferenceRules["Property_Range"]["prefixes"] , 
            antecedent =  InferenceRules["Property_Range"]["antecedent"] ,
            consequent = InferenceRules["Property_Range"]["consequent"] ,
            explanation = InferenceRules["Property_Range"]["explanation"]
        ),
        "Functional Data Property" : autonomic.Deductor(
            reference =  InferenceRules["Functional_Data_Property"]["reference"],
            resource = InferenceRules["Functional_Data_Property"]["resource"] , 
            prefixes = InferenceRules["Functional_Data_Property"]["prefixes"] , 
            antecedent =  InferenceRules["Functional_Data_Property"]["antecedent"] ,
            consequent = InferenceRules["Functional_Data_Property"]["consequent"] ,
            explanation = InferenceRules["Functional_Data_Property"]["explanation"]
        ),
        "Functional Object Property" : autonomic.Deductor(
            reference =  InferenceRules["Functional_Object_Property"]["reference"],
            resource = InferenceRules["Functional_Object_Property"]["resource"] , 
            prefixes = InferenceRules["Functional_Object_Property"]["prefixes"] , 
            antecedent =  InferenceRules["Functional_Object_Property"]["antecedent"] ,
            consequent = InferenceRules["Functional_Object_Property"]["consequent"] ,
            explanation = InferenceRules["Functional_Object_Property"]["explanation"]
        ),
        "Property Disjointness" : autonomic.Deductor(
            reference =  InferenceRules["Property_Disjointness"]["reference"],
            resource = InferenceRules["Property_Disjointness"]["resource"] , 
            prefixes = InferenceRules["Property_Disjointness"]["prefixes"] , 
            antecedent =  InferenceRules["Property_Disjointness"]["antecedent"] ,
            consequent = InferenceRules["Property_Disjointness"]["consequent"] ,
            explanation = InferenceRules["Property_Disjointness"]["explanation"]
        ),
        "Object Property Asymmetry" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Asymmetry"]["reference"],
            resource = InferenceRules["Object_Property_Asymmetry"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Asymmetry"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Asymmetry"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Asymmetry"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Asymmetry"]["explanation"]
        ),
        "Object Property Symmetry" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Symmetry"]["reference"],
            resource = InferenceRules["Object_Property_Symmetry"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Symmetry"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Symmetry"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Symmetry"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Symmetry"]["explanation"]
        ),
        "Object Property Irreflexivity": autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Irreflexivity"]["reference"],
            resource = InferenceRules["Object_Property_Irreflexivity"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Irreflexivity"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Irreflexivity"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Irreflexivity"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Irreflexivity"]["explanation"]
        ),
        "Class Inclusion" : autonomic.Deductor(
            reference =  InferenceRules["Class_Inclusion"]["reference"],
            resource = InferenceRules["Class_Inclusion"]["resource"] , 
            prefixes = InferenceRules["Class_Inclusion"]["prefixes"] , 
            antecedent =  InferenceRules["Class_Inclusion"]["antecedent"] ,
            consequent = InferenceRules["Class_Inclusion"]["consequent"] ,
            explanation = InferenceRules["Class_Inclusion"]["explanation"]
        ),
        "Individual Inclusion" : autonomic.Deductor(
            reference =  InferenceRules["Individual_Inclusion"]["reference"],
            resource = InferenceRules["Individual_Inclusion"]["resource"] , 
            prefixes = InferenceRules["Individual_Inclusion"]["prefixes"] , 
            antecedent =  InferenceRules["Individual_Inclusion"]["antecedent"] ,
            consequent = InferenceRules["Individual_Inclusion"]["consequent"] ,
            explanation = InferenceRules["Individual_Inclusion"]["explanation"]
        ),
        "Property Inclusion" : autonomic.Deductor(
            reference =  InferenceRules["Property_Inclusion"]["reference"],
            resource = InferenceRules["Property_Inclusion"]["resource"] , 
            prefixes = InferenceRules["Property_Inclusion"]["prefixes"] , 
            antecedent =  InferenceRules["Property_Inclusion"]["antecedent"] ,
            consequent = InferenceRules["Property_Inclusion"]["consequent"] ,
            explanation = InferenceRules["Property_Inclusion"]["explanation"]
        ),
        "Object Property Inclusion" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Inclusion"]["reference"],
            resource = InferenceRules["Object_Property_Inclusion"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Inclusion"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Inclusion"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Inclusion"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Inclusion"]["explanation"]
        ),
        "Data Property Inclusion" : autonomic.Deductor(
            reference =  InferenceRules["Data_Property_Inclusion"]["reference"],
            resource = InferenceRules["Data_Property_Inclusion"]["resource"] , 
            prefixes = InferenceRules["Data_Property_Inclusion"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Property_Inclusion"]["antecedent"] ,
            consequent = InferenceRules["Data_Property_Inclusion"]["consequent"] ,
            explanation = InferenceRules["Data_Property_Inclusion"]["explanation"]
        ),
        "Class Equivalence" : autonomic.Deductor(
            reference =  InferenceRules["Class_Equivalence"]["reference"],
            resource = InferenceRules["Class_Equivalence"]["resource"] , 
            prefixes = InferenceRules["Class_Equivalence"]["prefixes"] , 
            antecedent =  InferenceRules["Class_Equivalence"]["antecedent"] ,
            consequent = InferenceRules["Class_Equivalence"]["consequent"] ,
            explanation = InferenceRules["Class_Equivalence"]["explanation"]
        ),
        "Property Equivalence" : autonomic.Deductor(
            reference =  InferenceRules["Property_Equivalence"]["reference"],
            resource = InferenceRules["Property_Equivalence"]["resource"] , 
            prefixes = InferenceRules["Property_Equivalence"]["prefixes"] , 
            antecedent =  InferenceRules["Property_Equivalence"]["antecedent"] ,
            consequent = InferenceRules["Property_Equivalence"]["consequent"] ,
            explanation = InferenceRules["Property_Equivalence"]["explanation"]
        ),
        "Object Property Inversion" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Inversion"]["reference"],
            resource = InferenceRules["Object_Property_Inversion"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Inversion"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Inversion"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Inversion"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Inversion"]["explanation"]
        ),
        "Same Individual" : autonomic.Deductor(
            reference =  InferenceRules["Same_Individual"]["reference"],
            resource = InferenceRules["Same_Individual"]["resource"] , 
            prefixes = InferenceRules["Same_Individual"]["prefixes"] , 
            antecedent =  InferenceRules["Same_Individual"]["antecedent"] ,
            consequent = InferenceRules["Same_Individual"]["consequent"] ,
            explanation = InferenceRules["Same_Individual"]["explanation"]
        ),
        "Different Individuals" : autonomic.Deductor(
            reference =  InferenceRules["Different_Individuals"]["reference"],
            resource = InferenceRules["Different_Individuals"]["resource"] , 
            prefixes = InferenceRules["Different_Individuals"]["prefixes"] , 
            antecedent =  InferenceRules["Different_Individuals"]["antecedent"] ,
            consequent = InferenceRules["Different_Individuals"]["consequent"] ,
            explanation = InferenceRules["Different_Individuals"]["explanation"]
        ),
        "All Different Individuals" : autonomic.Deductor(
            reference =  InferenceRules["All_Different_Individuals"]["reference"],
            resource = InferenceRules["All_Different_Individuals"]["resource"] , 
            prefixes = InferenceRules["All_Different_Individuals"]["prefixes"] , 
            antecedent =  InferenceRules["All_Different_Individuals"]["antecedent"] ,
            consequent = InferenceRules["All_Different_Individuals"]["consequent"] ,
            explanation = InferenceRules["All_Different_Individuals"]["explanation"]
        ),
        "Class Assertion" : autonomic.Deductor(
            reference =  InferenceRules["Class_Assertion"]["reference"],
            resource = InferenceRules["Class_Assertion"]["resource"] , 
            prefixes = InferenceRules["Class_Assertion"]["prefixes"] , 
            antecedent =  InferenceRules["Class_Assertion"]["antecedent"] ,
            consequent = InferenceRules["Class_Assertion"]["consequent"] ,
            explanation = InferenceRules["Class_Assertion"]["explanation"]
        ),
#        "Positive Object Property Assertion" : autonomic.Deductor(
#            reference =  InferenceRules["Positive_Object_Property_Assertion"]["reference"],
#            resource = InferenceRules["Positive_Object_Property_Assertion"]["resource"] , 
#            prefixes = InferenceRules["Positive_Object_Property_Assertion"]["prefixes"] , 
#            antecedent =  InferenceRules["Positive_Object_Property_Assertion"]["antecedent"] ,
#            consequent = InferenceRules["Positive_Object_Property_Assertion"]["consequent"] ,
#            explanation = InferenceRules["Positive_Object_Property_Assertion"]["explanation"]
#        ),
#        "Positive Data Property Assertion" : autonomic.Deductor( 
#            reference =  InferenceRules["Positive_Data_Property_Assertion"]["reference"],
#            resource = InferenceRules["Positive_Data_Property_Assertion"]["resource"] , 
#            prefixes = InferenceRules["Positive_Data_Property_Assertion"]["prefixes"] , 
#            antecedent =  InferenceRules["Positive_Data_Property_Assertion"]["antecedent"] ,
#            consequent = InferenceRules["Positive_Data_Property_Assertion"]["consequent"] ,
#            explanation = InferenceRules["Positive_Data_Property_Assertion"]["explanation"]
#        ), # the previous two might just be s p o assertion
        "Negative Object Property Assertion" : autonomic.Deductor(
            reference =  InferenceRules["Negative_Object_Property_Assertion"]["reference"],
            resource = InferenceRules["Negative_Object_Property_Assertion"]["resource"] , 
            prefixes = InferenceRules["Negative_Object_Property_Assertion"]["prefixes"] , 
            antecedent =  InferenceRules["Negative_Object_Property_Assertion"]["antecedent"] ,
            consequent = InferenceRules["Negative_Object_Property_Assertion"]["consequent"] ,
            explanation = InferenceRules["Negative_Object_Property_Assertion"]["explanation"]
        ),
        "Negative Data Property Assertion" : autonomic.Deductor(
            reference =  InferenceRules["Negative_Data_Property_Assertion"]["reference"],
            resource = InferenceRules["Negative_Data_Property_Assertion"]["resource"] , 
            prefixes = InferenceRules["Negative_Data_Property_Assertion"]["prefixes"] , 
            antecedent =  InferenceRules["Negative_Data_Property_Assertion"]["antecedent"] ,
            consequent = InferenceRules["Negative_Data_Property_Assertion"]["consequent"] ,
            explanation = InferenceRules["Negative_Data_Property_Assertion"]["explanation"]
        ),
        "Keys" : autonomic.Deductor(
            reference =  InferenceRules["Keys"]["reference"],
            resource = InferenceRules["Keys"]["resource"] , 
            prefixes = InferenceRules["Keys"]["prefixes"] , 
            antecedent =  InferenceRules["Keys"]["antecedent"] ,
            consequent = InferenceRules["Keys"]["consequent"] ,
            explanation = InferenceRules["Keys"]["explanation"]
        ),
        "Inverse Functional Object Property" : autonomic.Deductor(
            reference =  InferenceRules["Inverse_Functional_Object_Property"]["reference"],
            resource = InferenceRules["Inverse_Functional_Object_Property"]["resource"] , 
            prefixes = InferenceRules["Inverse_Functional_Object_Property"]["prefixes"] , 
            antecedent =  InferenceRules["Inverse_Functional_Object_Property"]["antecedent"] ,
            consequent = InferenceRules["Inverse_Functional_Object_Property"]["consequent"] ,
            explanation = InferenceRules["Inverse_Functional_Object_Property"]["explanation"]
        ),
        "Object Some Values From" : autonomic.Deductor(
            reference =  InferenceRules["Object_Some_Values_From"]["reference"],
            resource = InferenceRules["Object_Some_Values_From"]["resource"] , 
            prefixes = InferenceRules["Object_Some_Values_From"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Some_Values_From"]["antecedent"] ,
            consequent = InferenceRules["Object_Some_Values_From"]["consequent"] ,
            explanation = InferenceRules["Object_Some_Values_From"]["explanation"]
        ),
        "Data Some Values From" : autonomic.Deductor(
            reference =  InferenceRules["Data_Some_Values_From"]["reference"],
            resource = InferenceRules["Data_Some_Values_From"]["resource"] , 
            prefixes = InferenceRules["Data_Some_Values_From"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Some_Values_From"]["antecedent"] ,
            consequent = InferenceRules["Data_Some_Values_From"]["consequent"] ,
            explanation = InferenceRules["Data_Some_Values_From"]["explanation"]
        ),
        "Object Has Self" : autonomic.Deductor(
            reference =  InferenceRules["Object_Has_Self"]["reference"],
            resource = InferenceRules["Object_Has_Self"]["resource"] , 
            prefixes = InferenceRules["Object_Has_Self"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Has_Self"]["antecedent"] ,
            consequent = InferenceRules["Object_Has_Self"]["consequent"] ,
            explanation = InferenceRules["Object_Has_Self"]["explanation"]
        ),
        "Object Has Value" : autonomic.Deductor(
            reference =  InferenceRules["Object_Has_Value"]["reference"],
            resource = InferenceRules["Object_Has_Value"]["resource"] , 
            prefixes = InferenceRules["Object_Has_Value"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Has_Value"]["antecedent"] ,
            consequent = InferenceRules["Object_Has_Value"]["consequent"] ,
            explanation = InferenceRules["Object_Has_Value"]["explanation"]
        ),
        "Data Has Value" : autonomic.Deductor(
            reference =  InferenceRules["Data_Has_Value"]["reference"],
            resource = InferenceRules["Data_Has_Value"]["resource"] , 
            prefixes = InferenceRules["Data_Has_Value"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Has_Value"]["antecedent"] ,
            consequent = InferenceRules["Data_Has_Value"]["consequent"] ,
            explanation = InferenceRules["Data_Has_Value"]["explanation"]
        ),
        "Object One Of Membership" : autonomic.Deductor(
            reference =  InferenceRules["Object_One_Of_Membership"]["reference"],
            resource = InferenceRules["Object_One_Of_Membership"]["resource"] , 
            prefixes = InferenceRules["Object_One_Of_Membership"]["prefixes"] , 
            antecedent =  InferenceRules["Object_One_Of_Membership"]["antecedent"] ,
            consequent = InferenceRules["Object_One_Of_Membership"]["consequent"] ,
            explanation = InferenceRules["Object_One_Of_Membership"]["explanation"]
        ),
        "Object One Of Inconsistency" : autonomic.Deductor(
            reference =  InferenceRules["Object_One_Of_Inconsistency"]["reference"],
            resource = InferenceRules["Object_One_Of_Inconsistency"]["resource"] , 
            prefixes = InferenceRules["Object_One_Of_Inconsistency"]["prefixes"] , 
            antecedent =  InferenceRules["Object_One_Of_Inconsistency"]["antecedent"] ,
            consequent = InferenceRules["Object_One_Of_Inconsistency"]["consequent"] ,
            explanation = InferenceRules["Object_One_Of_Inconsistency"]["explanation"]
        ),
        "Data One Of" : autonomic.Deductor(
            reference =  InferenceRules["Data_One_Of"]["reference"],
            resource = InferenceRules["Data_One_Of"]["resource"] , 
            prefixes = InferenceRules["Data_One_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Data_One_Of"]["antecedent"] ,
            consequent = InferenceRules["Data_One_Of"]["consequent"] ,
            explanation = InferenceRules["Data_One_Of"]["explanation"]
        ),
        "Object All Values From" : autonomic.Deductor(
            reference =  InferenceRules["Object_All_Values_From"]["reference"],
            resource = InferenceRules["Object_All_Values_From"]["resource"] , 
            prefixes = InferenceRules["Object_All_Values_From"]["prefixes"] , 
            antecedent =  InferenceRules["Object_All_Values_From"]["antecedent"] ,
            consequent = InferenceRules["Object_All_Values_From"]["consequent"] ,
            explanation = InferenceRules["Object_All_Values_From"]["explanation"]
        ),
        "Data All Values From" : autonomic.Deductor(
            reference =  InferenceRules["Data_All_Values_From"]["reference"],
            resource = InferenceRules["Data_All_Values_From"]["resource"] , 
            prefixes = InferenceRules["Data_All_Values_From"]["prefixes"] , 
            antecedent =  InferenceRules["Data_All_Values_From"]["antecedent"] ,
            consequent = InferenceRules["Data_All_Values_From"]["consequent"] ,
            explanation = InferenceRules["Data_All_Values_From"]["explanation"]
        ),
        "Object Max Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Object_Max_Cardinality"]["reference"],
            resource = InferenceRules["Object_Max_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Object_Max_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Max_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Object_Max_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Object_Max_Cardinality"]["explanation"]
        ),
        "Object Min Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Object_Min_Cardinality"]["reference"],
            resource = InferenceRules["Object_Min_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Object_Min_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Min_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Object_Min_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Object_Min_Cardinality"]["explanation"]
        ),
#        "Object Exact Cardinality (Max)" : autonomic.Deductor(
#            reference =  InferenceRules["Object_Exact_Cardinality_(Max)"]["reference"],
#            resource = InferenceRules["Object_Exact_Cardinality_(Max)"]["resource"] , 
#            prefixes = InferenceRules["Object_Exact_Cardinality_(Max)"]["prefixes"] , 
#            antecedent =  InferenceRules["Object_Exact_Cardinality_(Max)"]["antecedent"] ,
#            consequent = InferenceRules["Object_Exact_Cardinality_(Max)"]["consequent"] ,
#            explanation = InferenceRules["Object_Exact_Cardinality_(Max)"]["explanation"]
#        ),
#        "Object Exact Cardinality (Min)" : autonomic.Deductor(
#            reference =  InferenceRules["Object_Exact_Cardinality_(Min)"]["reference"],
#            resource = InferenceRules["Object_Exact_Cardinality_(Min)"]["resource"] , 
#            prefixes = InferenceRules["Object_Exact_Cardinality_(Min)"]["prefixes"] , 
#            antecedent =  InferenceRules["Object_Exact_Cardinality_(Min)"]["antecedent"] ,
#            consequent = InferenceRules["Object_Exact_Cardinality_(Min)"]["consequent"] ,
#            explanation = InferenceRules["Object_Exact_Cardinality_(Min)"]["explanation"]
#        ),
        "Data Max Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Data_Max_Cardinality"]["reference"],
            resource = InferenceRules["Data_Max_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Data_Max_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Max_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Data_Max_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Data_Max_Cardinality"]["explanation"]
        ),
        "Data Min Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Data_Min_Cardinality"]["reference"],
            resource = InferenceRules["Data_Min_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Data_Min_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Min_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Data_Min_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Data_Min_Cardinality"]["explanation"]
        ),
        "Data Exact Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Data_Exact_Cardinality"]["reference"],
            resource = InferenceRules["Data_Exact_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Data_Exact_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Exact_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Data_Exact_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Data_Exact_Cardinality"]["explanation"]
        ),
        "Object Union Of" : autonomic.Deductor(
            reference =  InferenceRules["Object_Union_Of"]["reference"],
            resource = InferenceRules["Object_Union_Of"]["resource"] , 
            prefixes = InferenceRules["Object_Union_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Union_Of"]["antecedent"] ,
            consequent = InferenceRules["Object_Union_Of"]["consequent"] ,
            explanation = InferenceRules["Object_Union_Of"]["explanation"]
        ),
        "Disjoint Union" : autonomic.Deductor(
            reference =  InferenceRules["Disjoint_Union"]["reference"],
            resource = InferenceRules["Disjoint_Union"]["resource"] , 
            prefixes = InferenceRules["Disjoint_Union"]["prefixes"] , 
            antecedent =  InferenceRules["Disjoint_Union"]["antecedent"] ,
            consequent = InferenceRules["Disjoint_Union"]["consequent"] ,
            explanation = InferenceRules["Disjoint_Union"]["explanation"]
        ),
        "Data Union Of" : autonomic.Deductor(
            reference =  InferenceRules["Data_Union_Of"]["reference"],
            resource = InferenceRules["Data_Union_Of"]["resource"] , 
            prefixes = InferenceRules["Data_Union_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Union_Of"]["antecedent"] ,
            consequent = InferenceRules["Data_Union_Of"]["consequent"] ,
            explanation = InferenceRules["Data_Union_Of"]["explanation"]
        ),
        "Object Complement Of" : autonomic.Deductor(
            reference =  InferenceRules["Object_Complement_Of"]["reference"],
            resource = InferenceRules["Object_Complement_Of"]["resource"] , 
            prefixes = InferenceRules["Object_Complement_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Complement_Of"]["antecedent"] ,
            consequent = InferenceRules["Object_Complement_Of"]["consequent"] ,
            explanation = InferenceRules["Object_Complement_Of"]["explanation"]
        ),
        "Data Complement Of" : autonomic.Deductor(
            reference =  InferenceRules["Data_Complement_Of"]["reference"],
            resource = InferenceRules["Data_Complement_Of"]["resource"] , 
            prefixes = InferenceRules["Data_Complement_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Complement_Of"]["antecedent"] ,
            consequent = InferenceRules["Data_Complement_Of"]["consequent"] ,
            explanation = InferenceRules["Data_Complement_Of"]["explanation"]
        ),
        "Object Property Complement Of" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Complement_Of"]["reference"],
            resource = InferenceRules["Object_Property_Complement_Of"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Complement_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Complement_Of"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Complement_Of"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Complement_Of"]["explanation"]
        ),
        "Data Property Complement Of" : autonomic.Deductor(
            reference =  InferenceRules["Data_Property_Complement_Of"]["reference"],
            resource = InferenceRules["Data_Property_Complement_Of"]["resource"] , 
            prefixes = InferenceRules["Data_Property_Complement_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Property_Complement_Of"]["antecedent"] ,
            consequent = InferenceRules["Data_Property_Complement_Of"]["consequent"] ,
            explanation = InferenceRules["Data_Property_Complement_Of"]["explanation"]
        ),
        "Object Intersection Of" : autonomic.Deductor(
            reference =  InferenceRules["Object_Intersection_Of"]["reference"],
            resource = InferenceRules["Object_Intersection_Of"]["resource"] , 
            prefixes = InferenceRules["Object_Intersection_Of"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Intersection_Of"]["antecedent"] ,
            consequent = InferenceRules["Object_Intersection_Of"]["consequent"] ,
            explanation = InferenceRules["Object_Intersection_Of"]["explanation"]
        ),
#        "Data Intersection Of" : autonomic.Deductor(
#            reference =  InferenceRules["Data_Intersection_Of"]["reference"],
#            resource = InferenceRules["Data_Intersection_Of"]["resource"] , 
#            prefixes = InferenceRules["Data_Intersection_Of"]["prefixes"] , 
#            antecedent =  InferenceRules["Data_Intersection_Of"]["antecedent"] ,
#            consequent = InferenceRules["Data_Intersection_Of"]["consequent"] ,
#            explanation = InferenceRules["Data_Intersection_Of"]["explanation"]
#        ),
        "Object Qualified Max Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Object_Qualified_Max_Cardinality"]["reference"],
            resource = InferenceRules["Object_Qualified_Max_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Object_Qualified_Max_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Qualified_Max_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Object_Qualified_Max_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Object_Qualified_Max_Cardinality"]["explanation"]
        ),
        "Object Qualified Min Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Object_Qualified_Min_Cardinality"]["reference"],
            resource = InferenceRules["Object_Qualified_Min_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Object_Qualified_Min_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Qualified_Min_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Object_Qualified_Min_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Object_Qualified_Min_Cardinality"]["explanation"]
        ),
#        "Object Qualified Exact Cardinality (Max)" : autonomic.Deductor( 
#            reference =  InferenceRules["Object_Qualified_Exact_Cardinality_(Max)"]["reference"],
#            resource = InferenceRules["Object_Qualified_Exact_Cardinality_(Max)"]["resource"] , 
#            prefixes = InferenceRules["Object_Qualified_Exact_Cardinality_(Max)"]["prefixes"] , 
#            antecedent =  InferenceRules["Object_Qualified_Exact_Cardinality_(Max)"]["antecedent"] ,
#            consequent = InferenceRules["Object_Qualified_Exact_Cardinality_(Max)"]["consequent"] ,
#            explanation = InferenceRules["Object_Qualified_Exact_Cardinality_(Max)"]["explanation"]
#        ),
#        "Object Qualified Exact Cardinality (Min)" : autonomic.Deductor(
#            reference =  InferenceRules["Object_Qualified_Exact_Cardinality_(Min)"]["reference"],
#            resource = InferenceRules["Object_Qualified_Exact_Cardinality_(Min)"]["resource"] , 
#            prefixes = InferenceRules["Object_Qualified_Exact_Cardinality_(Min)"]["prefixes"] , 
#            antecedent =  InferenceRules["Object_Qualified_Exact_Cardinality_(Min)"]["antecedent"] ,
#            consequent = InferenceRules["Object_Qualified_Exact_Cardinality_(Min)"]["consequent"] ,
#            explanation = InferenceRules["Object_Qualified_Exact_Cardinality_(Min)"]["explanation"]
#        ),
        "Data Qualified Max Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Data_Qualified_Max_Cardinality"]["reference"],
            resource = InferenceRules["Data_Qualified_Max_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Data_Qualified_Max_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Qualified_Max_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Data_Qualified_Max_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Data_Qualified_Max_Cardinality"]["explanation"]
        ),
        "Data Qualified Min Cardinality" : autonomic.Deductor(
            reference =  InferenceRules["Data_Qualified_Min_Cardinality"]["reference"],
            resource = InferenceRules["Data_Qualified_Min_Cardinality"]["resource"] , 
            prefixes = InferenceRules["Data_Qualified_Min_Cardinality"]["prefixes"] , 
            antecedent =  InferenceRules["Data_Qualified_Min_Cardinality"]["antecedent"] ,
            consequent = InferenceRules["Data_Qualified_Min_Cardinality"]["consequent"] ,
            explanation = InferenceRules["Data_Qualified_Min_Cardinality"]["explanation"]
        ),
#        "Data Qualified Exact Cardinality" : autonomic.Deductor(
#            reference =  InferenceRules["Data_Qualified_Exact_Cardinality"]["reference"],
#            resource = InferenceRules["Data_Qualified_Exact_Cardinality"]["resource"] , 
#            prefixes = InferenceRules["Data_Qualified_Exact_Cardinality"]["prefixes"] , 
#            antecedent =  InferenceRules["Data_Qualified_Exact_Cardinality"]["antecedent"] ,
#            consequent = InferenceRules["Data_Qualified_Exact_Cardinality"]["consequent"] ,
#            explanation = InferenceRules["Data_Qualified_Exact_Cardinality"]["explanation"]
#        ),
        "Datatype Restriction" : autonomic.Deductor(
            reference =  InferenceRules["Datatype_Restriction"]["reference"],
            resource = InferenceRules["Datatype_Restriction"]["resource"] , 
            prefixes = InferenceRules["Datatype_Restriction"]["prefixes"] , 
            antecedent =  InferenceRules["Datatype_Restriction"]["antecedent"] ,
            consequent = InferenceRules["Datatype_Restriction"]["consequent"] ,
            explanation = InferenceRules["Datatype_Restriction"]["explanation"]
        ),
        "All Disjoint Classes" : autonomic.Deductor(
            reference =  InferenceRules["All_Disjoint_Classes"]["reference"],
            resource = InferenceRules["All_Disjoint_Classes"]["resource"] , 
            prefixes = InferenceRules["All_Disjoint_Classes"]["prefixes"] , 
            antecedent =  InferenceRules["All_Disjoint_Classes"]["antecedent"] ,
            consequent = InferenceRules["All_Disjoint_Classes"]["consequent"] ,
            explanation = InferenceRules["All_Disjoint_Classes"]["explanation"]
        ),
        "All Disjoint Properties" : autonomic.Deductor(
            reference =  InferenceRules["All_Disjoint_Properties"]["reference"],
            resource = InferenceRules["All_Disjoint_Properties"]["resource"] , 
            prefixes = InferenceRules["All_Disjoint_Properties"]["prefixes"] , 
            antecedent =  InferenceRules["All_Disjoint_Properties"]["antecedent"] ,
            consequent = InferenceRules["All_Disjoint_Properties"]["consequent"] ,
            explanation = InferenceRules["All_Disjoint_Properties"]["explanation"]
        ),
        "Object Property Chain Inclusion" : autonomic.Deductor(
            reference =  InferenceRules["Object_Property_Chain_Inclusion"]["reference"],
            resource = InferenceRules["Object_Property_Chain_Inclusion"]["resource"] , 
            prefixes = InferenceRules["Object_Property_Chain_Inclusion"]["prefixes"] , 
            antecedent =  InferenceRules["Object_Property_Chain_Inclusion"]["antecedent"] ,
            consequent = InferenceRules["Object_Property_Chain_Inclusion"]["consequent"] ,
            explanation = InferenceRules["Object_Property_Chain_Inclusion"]["explanation"]
        ),
        "SDDAgent": autonomic.SDDAgent(), 
        "SETLr": autonomic.SETLr(),
        "SETLMaker": autonomic.SETLMaker(),
#        "Consistency Check" : hermit.ConsistencyCheck(),
#        "HTML2Text" : nlp.HTML2Text(),
#        "EntityExtractor" : nlp.EntityExtractor(),
#        "EntityResolver" : nlp.EntityResolver(),
#        "TF-IDF Calculator" : nlp.TFIDFCalculator(),
#        "SKOS Crawler" : autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related])
    },
    inference_tasks = [
#        dict ( name="SKOS Crawler",
#               service=autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related]),
#               schedule=dict(hour="1")
#              )
    ]
)

# config class for development environment
Dev = dict(Config)
Dev.update(dict(
    DEBUG = True,  # we want debug level output
    MAIL_DEBUG = True,
    # Works for the development virtual machine.
#    lod_prefix = "http://localhost:5000",
    DEBUG_TB_INTERCEPT_REDIRECTS = False,
    WTF_CSRF_ENABLED = False
))

# config class used during tests
Test = dict(Config)
del Test['admin_queryEndpoint']
del Test['admin_updateEndpoint']
del Test['knowledge_queryEndpoint']
del Test['knowledge_updateEndpoint']
Test.update(dict(
    nanopub_archive = {
        'depot.backend' : 'depot.io.memory.MemoryFileStorage'
    },

    DEFAULT_ANONYMOUS_READ = False,
    file_archive = {
        'depot.backend' : 'depot.io.memory.MemoryFileStorage'
    },
    TESTING = True,
    WTF_CSRF_ENABLED = False
))
