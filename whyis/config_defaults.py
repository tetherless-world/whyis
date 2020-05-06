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

# base config class; extend it to your needs.
Config = dict(
    # use DEBUG mode?
    DEBUG = False,

    site_name = "Whyis Knowledge Graph",

    # use TESTING mode?
    TESTING = False,

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
    namespaces = [
        importer.LinkedData(
            prefix = LOD_PREFIX+'/doi/',
            url = 'http://dx.doi.org/%s',
            headers={'Accept':'text/turtle'},
            format='turtle',
            postprocess_update= '''insert {
                graph ?g {
                    ?pub a <http://purl.org/ontology/bibo/AcademicArticle>.
                }
            } where {
                graph ?g {
                    ?pub <http://purl.org/ontology/bibo/doi> ?doi.
                }
            }
            '''
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
    active_profiles = ["OWL2 RL"],
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
            "Domain Restriction",
            "Range Restriction",
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
            #"Data Property Complement Of",
        ],
        "OWL2 RL" : [ # Note that only disjoint union and object property reflexitivity are not supported
            "Class Disjointness",
            "Object Property Transitivity",
            "Domain Restriction",
            "Range Restriction",
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
            "Data Max Cardinality",
            #"Data Min Cardinality",
            #"Data Exact Cardinality",
            # Disjunction  (ObjectUnionOf, and DataUnionOf)
        ]#, "OWL DL" : [   ]    # AllDifferent -> differentFrom individuals. Also need minInclusive, maxInclusive, (DisjointUnion not supported in RL)
    },
    inferencers  = {
        "Class Disjointness" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class .\n\t?resource rdf:type ?disjointClass .\n\t{?class owl:disjointWith ?disjointClass .} UNION {?disjointClass owl:disjointWith ?class .}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} is a disjoint with {{disjointClass}}, any resource that is an instance of {{class}} is not an instance of {{disjointClass}}. Therefore, since {{resource}} is an instance of {{class}}, it can not be an instance of {{disjointClass}}."
        ),
        "Object Property Transitivity" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?transitiveProperty ?o1 .\n\t?o1  ?transitiveProperty ?o2 .\n\t?transitiveProperty rdf:type owl:TransitiveProperty .",
            consequent = "?resource ?transitiveProperty ?o2 .",
            explanation = "Since {{transitiveProperty}} is a transitive object property, and the relationships {{resource}} {{transitiveProperty}} {{o1}} and {{o1}} {{transitiveProperty}} {{o2}} exist, then we can infer that {{resource}} {{transitiveProperty}} {{o2}}."
        ),
        "Object Property Reflexivity" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?reflexiveProperty ?o .\n\t?resource rdf:type ?type.\n\t?o rdf:type ?type.\n\t?reflexiveProperty rdf:type owl:ReflexiveProperty .",
            consequent = "?resource ?reflexiveProperty ?resource .",
            explanation = "Since {{resource}} has a {{reflexiveProperty}} assertion to {{o}}, {{resource}} and {{o}} are both of type {{type}}, and {{reflexiveProperty}} is a reflexive property, we can infer that {{resource}} {{reflexiveProperty}} {{resource}}."
        ),
        "Domain Restriction" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?p ?o .\n\t?p rdfs:domain ?class .",
            consequent = "?resource rdf:type ?class .",
            explanation = "Since the domain of {{p}} is {{class}}, this implies that {{resource}} is a {{class}}."
        ),
        "Range Restriction" : autonomic.Deductor(
            resource = "?resource",
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?p ?o .\n\t?p rdfs:range ?class .",
            consequent = "?o rdf:type ?class .",
            explanation = "Since the range of {{p}} is {{class}}, this implies that {{o}} is a {{class}}."
        ),
        "Functional Data Property" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?functionalProperty ?o1 .\n\t?functionalProperty rdf:type owl:DatatypeProperty , owl:FunctionalProperty . ?resource ?functionalProperty ?o2 .\n\tFILTER (str(?o1) !=  str(?o2))",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{functionalProperty}} is a functional data property, {{resource}} can only have one value for {{functionalProperty}}. Since {{resource}} {{functionalProperty}} both {{o1}} and {{o2}}, and {{o1}} is different from {{o2}}, an inconsistency occurs."
        ),
        "Functional Object Property" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?functionalProperty ?o1 .\n\t?functionalProperty rdf:type owl:ObjectProperty , owl:FunctionalProperty . ?resource ?functionalProperty ?o2 .\n\tFILTER (str(?o1) !=  str(?o2))",
            consequent = "?o1 owl:sameAs ?o2 .",
            explanation = "Since {{functionalProperty}} is a functional object property, {{resource}} can only have one value for {{functionalProperty}}. Since {{resource}} {{functionalProperty}} both {{o1}} and {{o2}}, we can infer that {{o1}} and {{o2}} must be the same individual."
        ),
        "Property Disjointness" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?p1 ?o1 .\n\t?resource ?p2 ?o2.\n\t?resource ?p1 ?o2 .\n\t{?p1 owl:propertyDisjointWith ?p2 .}UNION{?p2 owl:propertyDisjointWith ?p1 .}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since properties {p1} and {p2} are disjoint, {{resource}} having both {{p2}} {{o2}} as well as {{p1}} {{o2}} leads to an inconsistency. "
        ),
        "Object Property Asymmetry" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?asymmetricProperty ?o .\n\t?asymmetricProperty rdf:type owl:AsymmetricProperty . ?o ?asymmetricProperty ?resource .",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{asymmetricProperty}} is an asymmetric property, and {{resource}} {{asymmetricProperty}} {{o}}, then the assertion {{o}} {{asymmetricProperty}} {{resource}} results in an inconsistency."
        ),
        "Object Property Symmetry" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?symmetricProperty ?o .\n\t?symmetricProperty rdf:type owl:SymmetricProperty .",
            consequent = "?o ?symmetricProperty ?resource .",
            explanation = "Since {{symmetricProperty}} is a symmetric property, and {{resource}} {{symmetricProperty}} {{o}}, we can infer that {{o}} {{symmetricProperty}} {{resource}}."
        ),
        "Object Property Irreflexivity": autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?irreflexiveProperty ?o .\n\t?irreflexiveProperty rdf:type owl:IrreflexiveProperty .\n\t?resource ?irreflexiveProperty ?resource .",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{resource}} has a {{irreflexiveProperty}} assertion, and {{irreflexiveProperty}} is a irreflexive property, we can infer that the relationship {{resource}} {{irreflexiveProperty}} {{resource}} does not exist."
        ),
        "Class Inclusion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdfs:subClassOf ?class .\n\t?class rdfs:subClassOf+ ?superClass .",
            consequent = "?resource rdfs:subClassOf ?superClass .",
            explanation = "Since {{class}} is a subclass of {{superClass}}, any class that is a subclass of {{class}} is also a subclass of {{superClass}}. Therefore, {{resource}} is a subclass of {{superClass}}."
        ),
        "Individual Inclusion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class .\n\t?class rdfs:subClassOf+ ?superClass .",
            consequent = "?resource rdf:type ?superClass .",
            explanation = "Any instance of {{class}} is also an instance of {{superClass}}. Therefore, since {{resource}} is a {{class}}, it also is a {{superClass}}."
        ),
        "Property Inclusion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o .\n\t?p rdf:type owl:Property .\n\t?p rdfs:subPropertyOf+ ?superProperty .",
            consequent = "?resource ?superProperty ?o .",
            explanation = "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
        ),
        "Object Property Inclusion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o .\n\t?p rdf:type owl:ObjectProperty ;\n\t\trdfs:subPropertyOf+ ?superProperty .",
            consequent = "?resource ?superProperty ?o .",
            explanation = "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
        ),
        "Data Property Inclusion" : autonomic.Deductor(
            resource = "?resource",
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o .\n\t?p rdf:type owl:DatatypeProperty ;\n\t\trdfs:subPropertyOf+ ?superProperty .",
            consequent = "?resource ?superProperty ?o .",
            explanation = "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
        ),
        "Class Equivalence" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource a ?superClass.\n\t{?superClass owl:equivalentClass ?equivClass .} UNION {?equivClass owl:equivalentClass ?superClass .}", 
            consequent = "?resource rdf:type ?equivClass .",
            explanation = "{{superClass}} is equivalent to {{equivClass}}, so since {{resource}} is a {{superClass}}, it is also a {{equivClass}}."
        ),
        "Property Equivalence" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o .\n\t{?p owl:equivalentProperty ?equivProperty .} UNION {?equivProperty owl:equivalentProperty ?p . }", 
            consequent = "?resource ?equivProperty ?o .",
            explanation = "The properties {{p}} and {{equivProperty}} are equivalent. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{equivProperty}} {{o}}."
        ),
        "Object Property Inversion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o .\n\t?p rdf:type owl:ObjectProperty .\n\t{?p owl:inverseOf ?inverseProperty .} UNION {?inverseProperty owl:inverseOf ?p .}", 
            consequent = "?o ?inverseProperty ?resource .",
            explanation = "The object properties {{p}} and {{inverseProperty}} are inversely related to eachother. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{o}} {{inverseProperty}} {{resource}}."
        ),
        #"Assertions" (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
        "Same Individual" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource owl:sameAs ?individual .\n\t?resource ?p ?o .", 
            consequent = "?individual ?p ?o .",
            explanation = "Since {{resource}} is the same as {{individual}}, they share the same properties."#except maybe for annotation properties? should possibly add this check in
        ),
        "Different Individuals" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource owl:differentFrom ?individual ;\n\t\towl:sameAs ?individual .", 
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{resource}} is asserted as being different from {{individual}}, the assertion that {{resource}} is the same as {{individual}} leads to an inconsistency."
        ),
        "All Different" : autonomic.Deductor(
            resource = "?restriction", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?restriction rdf:type owl:AllDifferent ;\n\t\towl:distinctMembers ?list .\n\t?list rdf:rest*/rdf:first ?member .\n\t{\n\t\tSELECT DISTINCT ?item ?restrict WHERE {\n\t\t\t?restrict rdf:type owl:AllDifferent ;\n\t\t\t\towl:distinctMembers ?list .\n\t\t\t?list rdf:rest*/rdf:first ?item .}\n\t\t}\n\tFILTER(?restriction = ?restrict) \n\tFILTER(?member != ?item)", 
            consequent = "?member owl:differentFrom ?item .",
            explanation = "Since {{restriction}} is an all different restrictions with individuals listed in {{list}}, each member in {{list}} is different from each other member in the list."
        ),
        "Class Assertion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource rdf:type ?class .\n\t?class rdf:type owl:Class ;\n\t\trdfs:subClassOf+ ?superClass .", 
            consequent = "?resource rdf:type ?superClass .",
            explanation = "Since {{class}} is a subclass of {{superClass}}, any individual that is an instance of {{class}} is also an instance of {{superClass}}. Therefore, {{resource}} is an instance of {{superClass}}."
        ),
        "Positive Object Property Assertion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?objectProperty ?o.\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdf:type owl:Class;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\towl:onProperty ?objectProperty ;\n\t\t\t\towl:someValuesFrom owl:Thing ] .", 
            consequent = "?resource rdf:type ?class .",
            explanation = "Since {{resource}} {{objectProperty}} {{o}}, and {{class}} has an object property restriction on {{objectProperty}} to have any value that is an owl:Thing, we can infer that {{resource}} is a {{class}}."
        ),
        "Positive Data Property Assertion" : autonomic.Deductor( # Need to revisit to include data ranges
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?dataProperty ?o.\n\t?dataProperty rdf:type owl:DatatypeProperty .\n\t?class rdf:type owl:Class;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\towl:onProperty ?dataProperty ;\n\t\t\t\towl:someValuesFrom ?value ] .\n\tFILTER(DATATYPE(?o) = ?value)", 
            consequent = "?resource rdf:type ?class .",
            explanation = "Since {{resource}} {{dataProperty}} {{o}}, and {{class}} has an object property restriction on {{dataProperty}} to have a value of type {{value}}, and {{o}} is of type {{value}}, we can infer that {{resource}} is a {{class}}."
        ),
        "Negative Object Property Assertion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o.\n\t?p rdf:type owl:ObjectProperty .\n\t?x rdf:type owl:NegativePropertyAssertion ;\n\t\towl:sourceIndividual ?resource ;\n\t\towl:assertionProperty ?p ;\n\t\towl:targetIndividual ?o .", 
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since a negative object property assertion was made with source {{resource}}, object property {{p}}, and target individual {{o}}, the existence of {{resource}} {{p}} {{o}} results in an inconsistency."
        ),
        "Negative Data Property Assertion" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  "\t?resource ?p ?o.\n\t?p rdf:type owl:DatatypeProperty .\n\t?x rdf:type owl:NegativePropertyAssertion ;\n\t\towl:sourceIndividual ?resource ;\n\t\towl:assertionProperty ?p ;\n\t\towl:targetValue ?o .", 
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since a negative datatype property assertion was made with source {{resource}}, datatype property {{p}}, and target value {{o}}, the existence of {{resource}} {{p}} {{o}} results in an inconsistency."
        ),
        "Keys" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class .\n\t?class owl:hasKey ( ?keyProperty ) .\n\t?resource ?keyProperty ?keyValue.\n\t?individual rdf:type ?class.\n\t?individual ?keyProperty ?keyValue.",
            consequent = "?resource owl:sameAs ?individual .",
            explanation = "Since {{class}} has key {{keyProperty}}, {{resource}} and {{individual}} are both of type {{class}}, and {{resource}} and {{individual}} both {{keyProperty}} {{keyValue}}, then {{resource}} and {{individual}} must be the same."
        ),
        "Inverse Functional Object Property" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?invFunctionalProperty ?o .\n\t?individual ?invFunctionalProperty ?o .\n\t?invFunctionalProperty rdf:type owl:ObjectProperty , owl:InverseFunctionalProperty .",
            consequent = "?resource owl:sameAs ?individual",
            explanation = "Since {{invFunctionalProperty}} is an inverse functional property, and {{resource}} and {{individual}} both have the relationship {{invFunctionalProperty}} {{o}}, then we can infer that {{resource}} is the same as {{individual}}."
        ),
        #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom)
        "Object Some Values From" : autonomic.Deductor(# Should revisit this after confirming test case
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?objectProperty [ rdf:type ?valueclass ] .\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction;\n\t\towl:onProperty ?objectProperty;\n\t\towl:someValuesFrom ?valueclass ] .",
            consequent = "?resource rdf:type ?class .",
            explanation = "Since {{resource}} {{objectProperty}} an instance of {{valueclass}}, and {{class}} has a restriction on {{objectProperty}} to have some values from {{valueclass}}, we can infer that {{resource}} rdf:type {{class}}."
        ),
        "Data Some Values From" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ;\n\t\t?datatypeProperty ?val .\n\t?datatypeProperty rdf:type owl:DatatypeProperty .\n\t?class rdf:type owl:Class ;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?datatypeProperty ;\n\t\t\towl:someValuesFrom ?value ] .\n\tFILTER(DATATYPE(?val) != ?value)",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "{{resource}} {{datatypeProperty}} {{val}}, but {{val}} does not the same datatype {{value}} restricted for {{datatypeProperty}} in {{class}}. Since {{resource}} rdf:type {{class}}, an inconsistency occurs."
        ),#Data some and all values from behave the same as each other..? May need to revisit
        #"Self Restriction" (ObjectHasSelf): 
        "Object Has Self" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class .\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\t\towl:onProperty ?objectProperty ;\n\t\t\towl:hasSelf \"true\"^^xsd:boolean ] .",
            consequent = "?resource ?objectProperty ?resource .",
            explanation = "{{resource}} is of type {{class}}, which has a self restriction on the property {{objectProperty}}, allowing us to infer {{resource}} {{objectProperty}} {{resource}}."
        ),
        #"Individual Existential Quantification" (ObjectHasValue, DataHasValue)
        "Object Has Value" : autonomic.Deductor(
            resource = "?resource",
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class .\n\t?objectProperty rdf:type owl:ObjectProperty.\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?objectProperty ;\n\t\t\towl:hasValue ?object ] .",
            consequent = "?resource ?objectProperty?object .",
            explanation = "Since {{resource}} is of type {{class}}, which has a value restriction on {{objectProperty}} to have {{object}}, we can infer that {{resource}} {{objectProperty}} {{object}}."
        ),
        "Data Has Value" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource ?datatypeProperty ?value.\n\t?class owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?datatypeProperty ;\n\t\t\towl:hasValue ?value ].",
            consequent = "?resource rdf:type ?class .",
            explanation = "Since {{class}} is equivalent to the restriction on {{datatypeProperty}} to have value {{value}} and {{resource}} {{datatypeProperty}} {{value}}, we can infer that {{resource}} rdf:type {{class}}."
        ),#Note that only owl:equivalentClass results in inference, not rdfs:subClassOf
        #"Individual Enumeration" (ObjectOneOf, DataOneOf)
        "Object One Of" : autonomic.Deductor(#deals with lists rdf:rest+/rdf:first to traverse?
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type owl:Class ; owl:oneOf ?list .\n\t?list rdf:rest*/rdf:first ?member .",
            consequent = "?member rdf:type ?resource.",
            explanation = ""# need to address inconsistency when something not in the list is of type resource
        ),
        #"Data One Of" : autonomic.Deductor(
        #    resource = "?resource", 
        #    prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        #    antecedent =  "\t",
        #    consequent = "",
        #    explanation = ""
        #),
        #"Class Universal Quantification" (ObjectAllValuesFrom, DataAllValuesFrom)
        "Object All Values From" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?individual rdf:type ?class ; \n\t\t?objectProperty ?resource .\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction;\n\t\towl:onProperty ?objectProperty;\n\t\towl:allValuesFrom ?valueclass ] .",
            consequent = "?resource rdf:type ?valueclass.",
            explanation = "Since {{class}} has a restriction on {{objectProperty}} to have all values from {{valueclass}}, {{individual}} rdf:type {{class}}, and {{individual}} {{objectProperty}} {{resource}}, we can infer that {{resource}} rdf:type {{valueclass}}."
        ),
        "Data All Values From" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ;\n\t\t?datatypeProperty ?val .\n\t?datatypeProperty rdf:type owl:DatatypeProperty .\n\t?class rdf:type owl:Class ;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?datatypeProperty ;\n\t\t\towl:allValuesFrom ?value ] .\n\tFILTER(DATATYPE(?val)!= ?value)",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "{{resource}} {{datatypeProperty}} {{val}}, but {{val}} does not have the same datatype {{value}} restricted for {{datatypeProperty}} in {{class}}. Since {{resource}} rdf:type {{class}}, an inconsistency occurs."
        ),
        #"Cardinality Restriction" (ObjectMaxCardinality, ObjectMinCardinality, ObjectExactCardinality, DataMaxCardinality, DataMinCardinality, DataExactCardinality) 
        "Object Max Cardinality" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ;\n\t\t?objectProperty ?object .\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?objectProperty ;\n\t\t\towl:maxCardinality ?cardinalityValue ].\n\tFILTER(?objectCount > ?cardinalityValue)\n\t{\n\t\tSELECT DISTINCT (COUNT(DISTINCT ?object) as ?objectCount)\n\t\tWHERE {\n\t\t\t?resource rdf:type ?class ;\n\t\t\t\t?objectProperty ?object .\n\t\t\t?objectProperty rdf:type owl:ObjectProperty .\n\t\t\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?objectProperty ;\n\t\t\t\t\towl:maxCardinality ?cardinalityValue ].\n\t\t}\n\t}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{objectProperty}} is assigned a maximum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ),# Still need to check distinctness of object
        #"Object Min Cardinality" : autonomic.Deductor(
        #    resource = "?resource", 
        #    prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        #    antecedent =  "\t?resource rdf:type ?class ;\n\t\t?objectProperty ?object .\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?objectProperty ;\n\t\t\towl:minCardinality ?cardinalityValue ].\n\tFILTER(?objectCount < ?cardinalityValue)\n\t{\n\t\tSELECT DISTINCT (COUNT(DISTINCT ?object) as ?objectCount)\n\t\tWHERE {\n\t\t\t?resource rdf:type ?class ;\n\t\t\t\t?objectProperty ?object .\n\t\t\t?objectProperty rdf:type owl:ObjectProperty .\n\t\t\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?objectProperty ;\n\t\t\t\t\towl:minCardinality ?cardinalityValue ].\n\t\t}\n\t}",
        #    consequent = "",
        #    explanation = "Since {{objectProperty}} is assigned a minimum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is less than {{cardinalityValue}}, we can conclude the existence of additional assignments of {{objectProperty}} for {{resource}}."
        #),# Still need to check distinctness of object to determine what to return
        "Object Exact Cardinality" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ;\n\t\t?objectProperty ?object .\n\t?objectProperty rdf:type owl:ObjectProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?objectProperty ;\n\t\t\towl:cardinality ?cardinalityValue ].\n\tFILTER(?objectCount > ?cardinalityValue)\n\t{\n\t\tSELECT DISTINCT (COUNT(DISTINCT ?object) as ?objectCount)\n\t\tWHERE {\n\t\t\t?resource rdf:type ?class ;\n\t\t\t\t?objectProperty ?object .\n\t\t\t?objectProperty rdf:type owl:ObjectProperty .\n\t\t\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?objectProperty ;\n\t\t\t\t\towl:cardinality ?cardinalityValue ].\n\t\t}\n\t}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{objectProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ),# Still need to check distinctness of object -- This is currently only accounting for max. Need to account for min as well
        "Data Max Cardinality" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ;\n\t\t?dataProperty ?data .\n\t?dataProperty rdf:type owl:DatatypeProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?dataProperty ;\n\t\t\towl:maxCardinality ?cardinalityValue ].\n\tFILTER(?dataCount > ?cardinalityValue)\n\t{\n\t\tSELECT DISTINCT (COUNT(DISTINCT ?data) as ?dataCount)\n\t\tWHERE {\n\t\t\t?resource rdf:type ?class ;\n\t\t\t\t?dataProperty ?data .\n\t\t\t?dataProperty rdf:type owl:DatatypeProperty .\n\t\t\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?dataProperty ;\n\t\t\t\t\towl:maxCardinality ?cardinalityValue ].\n\t\t}\n\t}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{dataProperty}} is assigned a maximum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ),
        #"Data Min Cardinality" : autonomic.Deductor(
        #    resource = "?resource", 
        #    prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        #    antecedent =  "\t?resource rdf:type ?class ;\n\t\t?dataProperty ?data .\n\t?dataProperty rdf:type owl:DatatypeProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?dataProperty ;\n\t\t\towl:minCardinality ?cardinalityValue ].\n\tFILTER(?dataCount < ?cardinalityValue)\n\t{\n\t\tSELECT DISTINCT (COUNT(DISTINCT ?data) as ?dataCount)\n\t\tWHERE {\n\t\t\t?resource rdf:type ?class ;\n\t\t\t\t?dataProperty ?data .\n\t\t\t?dataProperty rdf:type owl:DatatypeProperty .\n\t\t\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?dataProperty ;\n\t\t\t\t\towl:minCardinality ?cardinalityValue ].\n\t\t}\n\t}",
        #    consequent = "?resource ?dataProperty :x .",
        #    explanation = "Since {{dataProperty}} is assigned a minimum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is less than {{cardinalityValue}}, we can conclude the existence of additional assignments of {{dataProperty}} for {{resource}}."
        #), # Still need to determine what to return, returning blanknode construction
        "Data Exact Cardinality" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ;\n\t\t?dataProperty ?data .\n\t?dataProperty rdf:type owl:DatatypeProperty .\n\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t[ rdf:type owl:Restriction ;\n\t\t\towl:onProperty ?dataProperty ;\n\t\t\towl:cardinality ?cardinalityValue ].\n\tFILTER(?dataCount > ?cardinalityValue)\n\t{\n\t\tSELECT DISTINCT (COUNT(DISTINCT ?data) as ?dataCount)\n\t\tWHERE {\n\t\t\t?resource rdf:type ?class ;\n\t\t\t\t?dataProperty ?data .\n\t\t\t?dataProperty rdf:type owl:DatatypeProperty .\n\t\t\t?class rdfs:subClassOf|owl:equivalentClass\n\t\t\t\t[ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?dataProperty ;\n\t\t\t\t\towl:cardinality ?cardinalityValue ].\n\t\t}\n\t}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{dataProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ), # -- This is currently only accounting for max. Need to account for min as well
        #"Disjunction" (ObjectUnionOf, DisjointUnion, and DataUnionOf)
        "Object Union Of" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type owl:Class ;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Class ;\n\t\t\t\towl:unionOf ?list ] .\n\t?list rdf:rest*/rdf:first ?member .",
            consequent = "?member rdfs:subClassOf ?resource .",
            explanation = "Since the class {{resource}} has a subclass or equivalent class relation with a class that comprises the union of {{list}}, which contains member {{member}}, we can infer that {{member}} is a subclass of {{resource}}."
        ),
        "Disjoint Union" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type owl:Class ;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Class ;\n\t\t\t\towl:disjointUnionOf ?list ] .\n\t?list rdf:rest*/rdf:first ?member .\n\t{\n\t\tSELECT DISTINCT ?item ?individual WHERE {\n\t\t\t?individual rdf:type owl:Class ;\n\t\t\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t\t\t[ rdf:type owl:Class ;\n\t\t\t\t\t\towl:disjointUnionOf ?list ] .\n\t\t\t?list rdf:rest*/rdf:first ?item .\n\t\t}\n\t}\n\tFILTER(?resource = ?individual)\n\tFILTER(?member != ?item)",
            consequent = "?member rdfs:subClassOf ?resource ; owl:disjointWith ?item .",
            explanation = "Since the class {{resource}} has a subclass or equivalent class relation with a class that comprises the disjoint union of {{list}}, which contains member {{member}}, we can infer that {{member}} is a subclass of {{resource}} and disjoint with the other members of the list."
        ),
        "Data Union Of" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?class rdf:type owl:Class ;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Class ;\n\t\t\t\towl:unionOf ?list ] .\n\t?list rdf:rest*/rdf:first ?member .\n\t?member rdf:type owl:Restriction ;\n\t\towl:onProperty ?dataProperty ;\n\t\towl:someValuesFrom ?datatype . ?dataProperty rdf:type owl:DatatypeProperty .\n\t?resource rdf:type ?class ;\n\t\t?dataProperty ?data .", #check if data is not one of the specified datatypes from the list, something like DATATYPE(?data)!=?datatype
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = ""
        ),
        "Object Complement Of" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?resource rdf:type ?class ,\n\t\t\t?complementClass .\n\t?class rdf:type owl:Class .\n\t?complementClass rdf:type owl:Class .{?class owl:complementOf ?complementClass .} UNION {?complementClass owl:complementOf ?class .}",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} and {{complementClass}} are complementary, {{resource}} being of type both {{class}} and {{complementClass}} leads to an inconsistency."
        ),
        "Object Property Complement Of" : autonomic.Deductor(
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  "\t?class rdf:type owl:Class ;\n\t\trdfs:subClassOf|owl:equivalentClass\n\t\t\t[ rdf:type owl:Class ;\n\t\t\t\towl:complementOf [ rdf:type owl:Restriction ;\n\t\t\t\t\towl:onProperty ?objectProperty ;\n\t\t\t\t\towl:someValuesFrom ?restrictedClass ] ] .\n\t?resource rdf:type ?class ;\n\t\t?objectProperty\n\t\t\t[ rdf:type ?restrictedClass ] .",
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} is a subclass of or is equivalent to a class with a complement restriction on the use of {{objectProperty}} to have values from {{restrictedClass}}, and {{resource}} is of type {{class}}, but has the link {{objectProperty}} to have values from an instance of {{restrictedClass}}, an inconsistency occurs." # do we also consider lists or complementary properties here?
        ),
        #"Data Property Complement Of" : autonomic.Deductor(
        #    resource = "?resource", 
        #    prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
        #    antecedent =  "\t",
        #    consequent = "?resource rdf:type owl:Nothing .",
        #    explanation = ""
        #),
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
