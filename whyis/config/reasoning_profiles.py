from whyis import autonomic

class_disjointness = autonomic.Deductor(
    resource="?resource",
    prefixes="",
    where = "\t?class owl:disjointWith ?disjointClass .\n\t?resource rdf:type ?class .\n\t?resource rdf:type ?disjointClass . ",
    construct="?resource rdf:type owl:Nothing . ",
    explanation="Since {{class}} is a disjoint with {{disjointClass}}, any resource that is an instance of {{class}} is not an instance of {{disjointClass}}. Therefore, {{resource}} is an instance of {{class}}, it is not an instance of {{disjointClass}}.")

object_property_transitivity = autonomic.Deductor(
    resource="?resource",
    prefixes="",
    where = "\t?resource ?transitiveProperty ?o1 .\n\t?o1  ?transitiveProperty ?o2 .\n\t?transitiveProperty rdf:type owl:TransitiveProperty .",
    construct="?resource ?transitiveProperty ?o2 .",
    explanation="Since {{transitiveProperty}} is a transitive object property, and the relationships {{resource}} {{transitiveProperty}} {{o1}} ans {{o1}} {{transitiveProperty}} {{o2}} exist, then we can infer that {{resource}} {{transitiveProperty}} {{o2}}.")

object_property_reflexivity = autonomic.Deductor(
    resource="?resource",
    prefixes="",
    where = "\t?resource ?reflexiveProperty ?o .\n\t?reflexiveProperty rdf:type owl:ReflexiveProperty .",
    construct="?resource ?reflexiveProperty ?resource .",
    explanation="Since {{resource}} has a {{reflexiveProperty}} assertion, and {{reflexiveProperty}} is a reflexive property, we can infer that {{resource}} {{reflexiveProperty}} {{resource}}.")

all = {
    "Class Disjointness": class_disjointness, # update explanation
    "Object Property Transitivity": object_property_transitivity,
    "Object Property Reflexivity": object_property_reflexivity,
    "Domain Restriction": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p rdfs:domain ?class .",
        construct="?resource rdf:type ?class",
        explanation="Since the domain of {{p}} is {{class}}, this implies that {{resource}} is a {{class}}."),
    "Range Restriction": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p rdfs:range ?class .",
        construct="?o rdf:type ?class",
        explanation="Since the range of {{p}} is {{class}}, this implies that {{o}} is a {{class}}."),
    "Functional Data Property" : autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?functionalProperty ?o1 .\n\t?functionalProperty rdf:type owl:DatatypeProperty , owl:FunctionalProperty . ?resource ?functionalProperty ?o1 .\n\tFILTER (str(?o1) != str(?o2))",
        construct="?resource rdf:type owl:Nothing .",
        explanation=""),
    "Functional Object Property": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?functionalProperty ?o1 .\n\t?functionalProperty rdf:type owl:ObjectProperty , owl:FunctionalProperty . ?resource ?functionalProperty ?o1 .\n\tFILTER (str(?o1) != str(?o2))",
        construct="?resource rdf:type owl:Nothing .",
        explanation=""),
    "Property Disjointness": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p1 ?o1 .\n\t?resource ?p2 ?o2.\n\t?p1 owl:propertyDisjointWith ?p2 .\n\t?resource ?p1 ?o2 .",
        construct="?resource rdf:type owl:Nothing .",
        explanation="Since properties {p1} and {p2} are disjoint, {{resource}} having both {{p2}} {{o2}} as well as {{p1}} {{o2}} leads to an inconsistency. "),
    "Object Property Asymmetry": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?asymmetricProperty ?o .\n\t?asymmetricProperty rdf:type owl:AsymmetricProperty . ?o ?asymmetricProperty ?resource .",
        construct="?resource rdf:type owl:Nothing .",
        explanation="Since {{asymmetricProperty}} is an asymmetric property, and {resource}} {{asymmetricProperty}} {{o}}, then the assertion {{o}} {{asymmetricProperty}} {{resource}} results in an inconsistency."),
    "Object Property Symmetry": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?symmetricProperty ?o .\n\t?symmetricProperty rdf:type owl:SymmetricProperty .",
        construct="?o ?symmetricProperty ?resource .",
        explanation="Since {{symmetricProperty}} is a symmetric property, and {resource}} {{symmetricProperty}} {{o}}, we can infer that {{o}} {{symmetricProperty}} {{resource}}."),
    "Object Property Irreflexivity":  autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?irreflexiveProperty ?o .\n\t?irreflexiveProperty rdf:type owl:IrreflexiveProperty .\n\t?resource ?irreflexiveProperty ?resource .",
        construct="?resource rdf:type owl:Nothing .",
        explanation="Since {{resource}} has a {{irreflexiveProperty}} assertion, and {{irreflexiveProperty}} is a irreflexive property, we can infer that the relationship {{resource}} {{irreflexiveProperty}} {{resource}} does not exist."),  # update explanation
    "Class Inclusion": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource rdfs:subClassOf ?class .\n\t?class rdfs:subClassOf+ ?superClass .",
        construct="?resource rdfs:subClassOf ?superClass .",
        explanation="Since {{class}} is a subclass of {{superClass}}, any class that is a subclass of {{class}} is also a subclass of {{superClass}}. Therefore, {{resource}} is a subclass of {{superClass}}."),
    "Individual Inclusion": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource rdf:type ?class .\n\t?class rdfs:subClassOf+ ?superClass .",
        construct="?resource rdf:type ?superClass .",
        explanation="Any instance of {{class}} is also an instance of {{superClass}}. Therefore, since {{resource}} is a {{class}}, it also is a {{superClass}}."),
    "Property Inclusion": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p rdf:type owl:Property .\n\t?p rdfs:subPropertyOf+ ?superProperty .",
        construct="?resource ?superProperty ?o .",
        explanation="Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."),
    "Object Property Inclusion": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p rdf:type owl:ObjectProperty .\n\t?p rdfs:subPropertyOf+ ?superProperty .",
        construct="?resource ?superProperty ?o .",
        explanation="Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."),
    "Data Property Inclusion": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p rdf:type owl:DatatypeProperty .\n\t?p rdfs:subPropertyOf+ ?superProperty .",
        construct="?resource ?superProperty ?o .",
        explanation="Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."),
    "Class Equivalence": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource a ?superClass.\n\t?superClass owl:equivalentClass ?equivClass .",
        construct="?resource a ?equivClass .",
        explanation="{{superClass}} is equivalent to {{equivClass}}, so since {{resource}} is a {{superClass}}, it is also a {{equivClass}}."),
    "Property Equivalence": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p owl:equivalentProperty ?equivProperty .",
        construct="?resource ?equivProperty ?o .",
        explanation="The properties {{p}} and {{equivProperty}} are equivalent. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{equivProperty}} {{o}}."),
    "Object Property Inversion": autonomic.Deductor(
        resource="?resource",
        prefixes="",
        where = "\t?resource ?p ?o .\n\t?p rdf:type owl:ObjectProperty .\n\t?p owl:inverseOf ?inverseProperty .",
        construct="?o ?inverseProperty ?resource .",
        explanation="The object properties {{p}} and {{inverseProperty}} are inversely related to eachother. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{o}} {{inverseProperty}} {{resource}}."),
    #"Assertions" (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
    #"Keys" (HasKey): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t?resource owl:hasKey ?key .",
    #    construct="",
    #    explanation=""),
    #"Inverse Functional Object Property"(InverseFunctionalObjectProperty): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t?resource ?invFunctionalProperty ?o .\n\t?invFunctionalProperty rdf:type owl:ObjectProperty , owl:InverseFunctionalProperty .",
    #    construct="",
    #    explanation=""),
    #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t",
    #    construct="",
    #    explanation=""),
    #"Self Restriction" (ObjectHasSelf): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t",
    #    construct="",
    #    explanation=""),
    #"Individual Existential Quantification" (ObjectHasValue, DataHasValue): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t",
    #    construct="",
    #    explanation=""),
    #"Individual Enumeration" (ObjectOneOf, DataOneOf): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t",
    #    construct="",
    #    explanation=""),
    #"Class Universal Quantification" (ObjectAllValuesFrom, DataAllValuesFrom): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t",
    #    construct="",
    #    explanation=""),
    #"Cardinality Restriction" (ObjectMaxCardinality, ObjectMinCardinality, ObjectExactCardinality, DataMaxCardinality, DataMinCardinality, DataExactCardinality)
    #"Disjunction" (ObjectUnionOf, DisjointUnion, and DataUnionOf): autonomic.Deductor(
    #    resource="?resource",
    #    prefixes="",
    #    where = "\t",
    #    construct="",
    #    explanation=""),
}

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
            "Domain Restriction",
            "Range Restriction",
            "Functional Data Property",
            #"Assertions", (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
            #"Keys",
        ],
        "OWL2 QL" : [
            "Class Inclusion",
            "Class Equivalence",
            "Class Disjointness",
            "Object Property Inversion",
            "Property Inclusion",
            "Domain Restriction",
            "Range Restriction",
            "Property Disjointness",
            "Object Property Symmetry",
            "Object Property Reflexivity",
            "Object Property Irreflexivity",
            "Object Property Asymmetry",
            #"Assertions", (DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, and DataPropertyAssertion)
        ],
        "OWL2 RL" : [
            "Class Disjointness" ,
            "Object Property Transitivity" ,
            "Domain Restriction" ,
            "Range Restriction" ,
            "Functional Data Property" ,
            "Functional Object Property",
            "Property Disjointness" ,
            "Object Property Symmetry" ,
            "Object Property Asymmetry",
            "Class Inclusion" ,
            "Property Inclusion" ,
            "Object Property Inclusion" ,
            "Data Property Inclusion" ,
            "Class Equivalence" ,
            "Property Equivalence" ,
            "Object Property Inversion",
            #"Assertions" (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
            #"Keys" ,
            #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom)
            #"Self Restriction" (ObjectHasSelf)
            #"Individual Existential Quantification" (ObjectHasValue, DataHasValue)
            #"Individual Enumeration" (ObjectOneOf, DataOneOf)
            #"Class Universal Quantification" (ObjectAllValuesFrom, DataAllValuesFrom)
            #"Cardinality Restriction" (ObjectMaxCardinality, ObjectMinCardinality, ObjectExactCardinality, DataMaxCardinality, DataMinCardinality, DataExactCardinality)
        ]
}
