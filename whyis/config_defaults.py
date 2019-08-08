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
    },
    inferencers = {
        "SETLr": autonomic.SETLr(),
        "Class Disjointness": autonomic.Deductor(
            resource="?resource", 
            prefixes="", 
            where = "\t?class owl:disjointWith ?disjointClass .\n\t?resource rdf:type ?class .\n\t?resource rdf:type ?disjointClass . ",
            construct="?resource rdf:type owl:Nothing . ",
            explanation="Since {{class}} is a disjoint with {{disjointClass}}, any resource that is an instance of {{class}} is not an instance of {{disjointClass}}. Therefore, {{resource}} is an instance of {{class}}, it is not an instance of {{disjointClass}}."), # update explanation
        "Object Property Transitivity": autonomic.Deductor(
            resource="?resource", 
            prefixes="", 
            where = "\t?resource ?transitiveProperty ?o1 .\n\t?o1  ?transitiveProperty ?o2 .\n\t?transitiveProperty rdf:type owl:TransitiveProperty .",
            construct="?resource ?transitiveProperty ?o2 .",
            explanation="Since {{transitiveProperty}} is a transitive object property, and the relationships {{resource}} {{transitiveProperty}} {{o1}} ans {{o1}} {{transitiveProperty}} {{o2}} exist, then we can infer that {{resource}} {{transitiveProperty}} {{o2}}."),
        "Object Property Reflexivity": autonomic.Deductor(
            resource="?resource", 
            prefixes="", 
            where = "\t?resource ?reflexiveProperty ?o .\n\t?reflexiveProperty rdf:type owl:ReflexiveProperty .",
            construct="?resource ?reflexiveProperty ?resource .",
            explanation="Since {{resource}} has a {{reflexiveProperty}} assertion, and {{reflexiveProperty}} is a reflexive property, we can infer that {{resource}} {{reflexiveProperty}} {{resource}}."),
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
