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

    CACHE_TYPE = "simple", # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 0,

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
            #"Data Property Complement Of",
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
        ]#, "OWL DL" : [   ]    # "All Different Individuals" -> differentFrom individuals. AllDisjointClasses --> pairwise disjoint classes . Also need minInclusive, maxInclusive, (DisjointUnion not supported in RL), ObjectPropertyChainInclusion
    },
    inferencers  = {
        "Class Disjointness" : autonomic.Deductor(
            reference = "Class Disjointness",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class .
    ?resource rdf:type ?disjointClass .
    { ?class owl:disjointWith ?disjointClass . } 
        UNION
    { ?disjointClass owl:disjointWith ?class . }''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} is a disjoint with {{disjointClass}}, any resource that is an instance of {{class}} is not an instance of {{disjointClass}}. Therefore, since {{resource}} is an instance of {{class}}, it can not be an instance of {{disjointClass}}."
        ),
        "Object Property Transitivity" : autonomic.Deductor(
            reference = "Object Property Transitivity",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?transitiveProperty ?o1 .
    ?o1  ?transitiveProperty ?o2 .
    ?transitiveProperty rdf:type owl:TransitiveProperty .''',
            consequent = "?resource ?transitiveProperty ?o2 .",
            explanation = "Since {{transitiveProperty}} is a transitive object property, and the relationships {{resource}} {{transitiveProperty}} {{o1}} and {{o1}} {{transitiveProperty}} {{o2}} exist, then we can infer that {{resource}} {{transitiveProperty}} {{o2}}."
        ),
        "Object Property Reflexivity" : autonomic.Deductor(
            reference = "Object Property Reflexivity",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?type ;
        ?reflexiveProperty ?o .
    ?o rdf:type ?type.
    ?reflexiveProperty rdf:type owl:ReflexiveProperty .''',
            consequent = "?resource ?reflexiveProperty ?resource .",
            explanation = "Since {{resource}} has a {{reflexiveProperty}} assertion to {{o}}, {{resource}} and {{o}} are both of type {{type}}, and {{reflexiveProperty}} is a reflexive property, we can infer that {{resource}} {{reflexiveProperty}} {{resource}}."
        ),
        "Property Domain" : autonomic.Deductor(
            reference = "Property Domain",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?p ?o .
    ?p rdfs:domain ?class .''',
            consequent = "?resource rdf:type ?class .",
            explanation = "Since the domain of {{p}} is {{class}}, this implies that {{resource}} is a {{class}}."
        ),
        "Property Range" : autonomic.Deductor(
            reference = "Property Range",
            resource = "?resource",
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?p ?o .
    ?p rdfs:range ?class .''',
            consequent = "?o rdf:type ?class .",
            explanation = "Since the range of {{p}} is {{class}}, this implies that {{o}} is a {{class}}."
        ),
        "Functional Data Property" : autonomic.Deductor(
            reference = "Functional Data Property",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?functionalProperty ?o1 ,
            ?o2 .
    ?functionalProperty rdf:type owl:DatatypeProperty ,
            owl:FunctionalProperty .
    FILTER (str(?o1) !=  str(?o2))''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{functionalProperty}} is a functional data property, {{resource}} can only have one value for {{functionalProperty}}. Since {{resource}} {{functionalProperty}} both {{o1}} and {{o2}}, and {{o1}} is different from {{o2}}, an inconsistency occurs."
        ),
        "Functional Object Property" : autonomic.Deductor(
            reference = "Functional Object Property",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?functionalProperty ?o1 ,
            ?o2 .
    ?functionalProperty rdf:type owl:ObjectProperty , 
            owl:FunctionalProperty .
    FILTER (str(?o1) !=  str(?o2))''',
            consequent = "?o1 owl:sameAs ?o2 .",
            explanation = "Since {{functionalProperty}} is a functional object property, {{resource}} can only have one value for {{functionalProperty}}. Since {{resource}} {{functionalProperty}} both {{o1}} and {{o2}}, we can infer that {{o1}} and {{o2}} must be the same individual."
        ),
        "Property Disjointness" : autonomic.Deductor(
            reference = "Property Disjointness",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?p1 ?o1 ,
            ?o2 .
    ?resource ?p2 ?o2.
    {?p1 owl:propertyDisjointWith ?p2 .}
        UNION
    {?p2 owl:propertyDisjointWith ?p1 .}''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since properties {p1} and {p2} are disjoint, {{resource}} having both {{p2}} {{o2}} as well as {{p1}} {{o2}} leads to an inconsistency. "
        ),
        "Object Property Asymmetry" : autonomic.Deductor(
            reference = "Object Property Asymmetry",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?asymmetricProperty ?o .
    ?asymmetricProperty rdf:type owl:AsymmetricProperty .
    ?o ?asymmetricProperty ?resource .''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{asymmetricProperty}} is an asymmetric property, and {{resource}} {{asymmetricProperty}} {{o}}, then the assertion {{o}} {{asymmetricProperty}} {{resource}} results in an inconsistency."
        ),
        "Object Property Symmetry" : autonomic.Deductor(
            reference = "Object Property Symmetry",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?symmetricProperty ?o .
    ?symmetricProperty rdf:type owl:SymmetricProperty .''',
            consequent = "?o ?symmetricProperty ?resource .",
            explanation = "Since {{symmetricProperty}} is a symmetric property, and {{resource}} {{symmetricProperty}} {{o}}, we can infer that {{o}} {{symmetricProperty}} {{resource}}."
        ),
        "Object Property Irreflexivity": autonomic.Deductor(
            reference = "Object Property Irreflexivity",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?irreflexiveProperty ?o .
    ?irreflexiveProperty rdf:type owl:IrreflexiveProperty .
    ?resource ?irreflexiveProperty ?resource .''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{resource}} has a {{irreflexiveProperty}} assertion, and {{irreflexiveProperty}} is a irreflexive property, we can infer that the relationship {{resource}} {{irreflexiveProperty}} {{resource}} does not exist."
        ),
        "Class Inclusion" : autonomic.Deductor(
            reference = "Class Inclusion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdfs:subClassOf ?class .
    ?class rdfs:subClassOf+ ?superClass .''',
            consequent = "?resource rdfs:subClassOf ?superClass .",
            explanation = "Since {{class}} is a subclass of {{superClass}}, any class that is a subclass of {{class}} is also a subclass of {{superClass}}. Therefore, {{resource}} is a subclass of {{superClass}}."
        ),
        "Individual Inclusion" : autonomic.Deductor(
            reference = "Individual Inclusion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class .
    ?class rdfs:subClassOf+ ?superClass .''',
            consequent = "?resource rdf:type ?superClass .",
            explanation = "Any instance of {{class}} is also an instance of {{superClass}}. Therefore, since {{resource}} is a {{class}}, it also is a {{superClass}}."
        ),
        "Property Inclusion" : autonomic.Deductor(
            reference = "Property Inclusion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o .
    ?p rdf:type owl:Property ;
        rdfs:subPropertyOf+ ?superProperty .''',
            consequent = "?resource ?superProperty ?o .",
            explanation = "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
        ),
        "Object Property Inclusion" : autonomic.Deductor(
            reference = "Object Property Inclusion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o .
    ?p rdf:type owl:ObjectProperty ;
        rdfs:subPropertyOf+ ?superProperty .''',
            consequent = "?resource ?superProperty ?o .",
            explanation = "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
        ),
        "Data Property Inclusion" : autonomic.Deductor(
            reference = "Data Property Inclusion",
            resource = "?resource",
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o .
    ?p rdf:type owl:DatatypeProperty ;
        rdfs:subPropertyOf+ ?superProperty .''',
            consequent = "?resource ?superProperty ?o .",
            explanation = "Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."
        ),
        "Class Equivalence" : autonomic.Deductor(
            reference = "Class Equivalence",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource rdf:type ?superClass.
    {?superClass owl:equivalentClass ?equivClass .}
        UNION
    {?equivClass owl:equivalentClass ?superClass .}''', 
            consequent = "?resource rdf:type ?equivClass .",
            explanation = "{{superClass}} is equivalent to {{equivClass}}, so since {{resource}} is a {{superClass}}, it is also a {{equivClass}}."
        ),
        "Property Equivalence" : autonomic.Deductor(
            reference = "Property Equivalence",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o .
    {?p owl:equivalentProperty ?equivProperty .}
        UNION
    {?equivProperty owl:equivalentProperty ?p . }''', 
            consequent = "?resource ?equivProperty ?o .",
            explanation = "The properties {{p}} and {{equivProperty}} are equivalent. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{equivProperty}} {{o}}."
        ),
        "Object Property Inversion" : autonomic.Deductor(
            reference = "Object Property Inversion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o .
    ?p rdf:type owl:ObjectProperty .
    {?p owl:inverseOf ?inverseProperty .}
        UNION
    {?inverseProperty owl:inverseOf ?p .}''', 
            consequent = "?o ?inverseProperty ?resource .",
            explanation = "The object properties {{p}} and {{inverseProperty}} are inversely related to eachother. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{o}} {{inverseProperty}} {{resource}}."
        ),
        #"Assertions" (SameIndividual, DifferentIndividuals, ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, NegativeObjectPropertyAssertion, and NegativeDataPropertyAssertion)
        "Same Individual" : autonomic.Deductor(
            reference = "Same Individual",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource owl:sameAs ?individual .
    ?resource ?p ?o .''', 
            consequent = "?individual ?p ?o .",
            explanation = "Since {{resource}} is the same as {{individual}}, they share the same properties."#except maybe for annotation properties? should possibly add this check in
        ),
        "Different Individuals" : autonomic.Deductor(
            reference = "Different Individuals",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource owl:differentFrom ?individual ;
        owl:sameAs ?individual .''', 
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{resource}} is asserted as being different from {{individual}}, the assertion that {{resource}} is the same as {{individual}} leads to an inconsistency."
        ),
        "All Different Individuals" : autonomic.Deductor(
            reference = "All Different Individuals",
            resource = "?restriction", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
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
            consequent = "?member owl:differentFrom ?item .",
            explanation = "Since {{restriction}} is an all different restriction with individuals listed in {{list}}, each member in {{list}} is different from each other member in the list."
        ),
        "Class Assertion" : autonomic.Deductor(
            reference = "Class Assertion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource rdf:type ?class .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf+ ?superClass .''', 
            consequent = "?resource rdf:type ?superClass .",
            explanation = "Since {{class}} is a subclass of {{superClass}}, any individual that is an instance of {{class}} is also an instance of {{superClass}}. Therefore, {{resource}} is an instance of {{superClass}}."
        ),
#        "Positive Object Property Assertion" : autonomic.Deductor(
#            reference = "Positive Object Property Assertion",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
#            antecedent =  '''
#    ?resource ?objectProperty ?o.
#    ?objectProperty rdf:type owl:ObjectProperty .
#    ?class rdf:type owl:Class;
#        rdfs:subClassOf|owl:equivalentClass
#            [ rdf:type owl:Restriction ;
#                owl:onProperty ?objectProperty ;
#                owl:someValuesFrom owl:Thing ] .''',#may need to come back to this 
#            consequent = "?resource rdf:type ?class .",
#            explanation = "Since {{resource}} {{objectProperty}} {{o}}, and {{class}} has an object property restriction on {{objectProperty}} to have any value that is an owl:Thing, we can infer that {{resource}} is a {{class}}."
#        ),
#        "Positive Data Property Assertion" : autonomic.Deductor( # Need to revisit to include data ranges
#            reference = "Positive Data Property Assertion",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
#            antecedent =  '''
#    ?resource ?dataProperty ?o.
#    ?dataProperty rdf:type owl:DatatypeProperty .
#    ?class rdf:type owl:Class;
#        rdfs:subClassOf|owl:equivalentClass
#            [ rdf:type owl:Restriction ;
#                owl:onProperty ?dataProperty ;
#                owl:someValuesFrom ?value ] .
#    FILTER(DATATYPE(?o) = ?value)''', 
#            consequent = "?resource rdf:type ?class .",
#            explanation = "Since {{resource}} {{dataProperty}} {{o}}, and {{class}} has an object property restriction on {{dataProperty}} to have a value of type {{value}}, and {{o}} is of type {{value}}, we can infer that {{resource}} is a {{class}}."
#        ), # the previous two might just be s p o assertion
        "Negative Object Property Assertion" : autonomic.Deductor(
            reference = "Negative Object Property Assertion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o.
    ?p rdf:type owl:ObjectProperty .
    ?x rdf:type owl:NegativePropertyAssertion ;
        owl:sourceIndividual ?resource ;
        owl:assertionProperty ?p ;
        owl:targetIndividual ?o .''', 
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since a negative object property assertion was made with source {{resource}}, object property {{p}}, and target individual {{o}}, the existence of {{resource}} {{p}} {{o}} results in an inconsistency."
        ),
        "Negative Data Property Assertion" : autonomic.Deductor(
            reference = "Negative Data Property Assertion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"},
            antecedent =  '''
    ?resource ?p ?o.
    ?p rdf:type owl:DatatypeProperty .
    ?x rdf:type owl:NegativePropertyAssertion ;
        owl:sourceIndividual ?resource ;
        owl:assertionProperty ?p ;
        owl:targetValue ?o .''', 
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since a negative datatype property assertion was made with source {{resource}}, datatype property {{p}}, and target value {{o}}, the existence of {{resource}} {{p}} {{o}} results in an inconsistency."
        ),
        "Keys" : autonomic.Deductor(
            reference = "Keys",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class ;
        ?keyProperty ?keyValue.
    ?class rdf:type owl:Class ;
        owl:hasKey ( ?keyProperty ) .
    ?individual rdf:type ?class ;
        ?keyProperty ?keyValue.''',
            consequent = "?resource owl:sameAs ?individual .",
            explanation = "Since {{class}} has key {{keyProperty}}, {{resource}} and {{individual}} are both of type {{class}}, and {{resource}} and {{individual}} both {{keyProperty}} {{keyValue}}, then {{resource}} and {{individual}} must be the same."
        ),
        "Inverse Functional Object Property" : autonomic.Deductor(
            reference = "Inverse Functional Object Property",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?invFunctionalProperty ?o .
    ?individual ?invFunctionalProperty ?o .
    ?invFunctionalProperty rdf:type owl:ObjectProperty ,
            owl:InverseFunctionalProperty .''',
            consequent = "?resource owl:sameAs ?individual",
            explanation = "Since {{invFunctionalProperty}} is an inverse functional property, and {{resource}} and {{individual}} both have the relationship {{invFunctionalProperty}} {{o}}, then we can infer that {{resource}} is the same as {{individual}}."
        ),
        #"Class Existential Quantification" (ObjectSomeValuesFrom and DataSomeValuesFrom)
        "Object Some Values From" : autonomic.Deductor(# Should revisit this after confirming test case
            reference = "Object Some Values From",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?objectProperty
        [ rdf:type ?valueclass ] .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction;
            owl:onProperty ?objectProperty;
            owl:someValuesFrom ?valueclass ] .''',
            consequent = "?resource rdf:type ?class .",
            explanation = "Since {{resource}} {{objectProperty}} an instance of {{valueclass}}, and {{class}} has a restriction on {{objectProperty}} to have some values from {{valueclass}}, we can infer that {{resource}} rdf:type {{class}}."
        ),
        "Data Some Values From" : autonomic.Deductor(
            reference = "Data Some Values From",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class ;
        ?datatypeProperty ?val .
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?datatypeProperty ;
                owl:someValuesFrom ?value ] .
    FILTER(DATATYPE(?val) != ?value)''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "{{resource}} {{datatypeProperty}} {{val}}, but {{val}} does not the same datatype {{value}} restricted for {{datatypeProperty}} in {{class}}. Since {{resource}} rdf:type {{class}}, an inconsistency occurs."
        ),#Data some and all values from behave the same as each other..? May need to revisit
        #"Self Restriction" (ObjectHasSelf): 
        "Object Has Self" : autonomic.Deductor(
            reference = "Object Has Self",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:hasSelf \"true\"^^xsd:boolean ] .''',
            consequent = "?resource ?objectProperty ?resource .",
            explanation = "{{resource}} is of type {{class}}, which has a self restriction on the property {{objectProperty}}, allowing us to infer {{resource}} {{objectProperty}} {{resource}}."
        ),
        #"Individual Existential Quantification" (ObjectHasValue, DataHasValue)
        "Object Has Value" : autonomic.Deductor(
            reference = "Object Has Value",
            resource = "?resource",
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class .
    ?objectProperty rdf:type owl:ObjectProperty.
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?objectProperty ;
            owl:hasValue ?object ] .''',
            consequent = "?resource ?objectProperty?object .",
            explanation = "Since {{resource}} is of type {{class}}, which has a value restriction on {{objectProperty}} to have {{object}}, we can infer that {{resource}} {{objectProperty}} {{object}}."
        ),
        "Data Has Value" : autonomic.Deductor(
            reference = "Data Has Value",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource ?datatypeProperty ?value.
    ?class owl:equivalentClass
        [ rdf:type owl:Restriction ;
            owl:onProperty ?datatypeProperty ;
            owl:hasValue ?value ].''',
            consequent = "?resource rdf:type ?class .",
            explanation = "Since {{class}} is equivalent to the restriction on {{datatypeProperty}} to have value {{value}} and {{resource}} {{datatypeProperty}} {{value}}, we can infer that {{resource}} rdf:type {{class}}."
        ),#Note that only owl:equivalentClass results in inference, not rdfs:subClassOf
        #"Individual Enumeration" (ObjectOneOf, DataOneOf)
        "Object One Of Membership" : autonomic.Deductor(#deals with lists rdf:rest+/rdf:first to traverse?
            reference = "Object One Of Membership",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type owl:Class ;
        owl:oneOf ?list .
    ?list rdf:rest*/rdf:first ?member .''',
            consequent = "?member rdf:type ?resource .",
            explanation = "Since {{resource}} has a one of relationship with {{list}}, the member {{member}} in {{list}} is of type {{resource}}."
        ),
        "Object One Of Inconsistency" : autonomic.Deductor(
            reference = "Object One Of Inconsistency",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
        } #GROUP BY ?concept ?individual
    }
    FILTER(?conceptCount=0)
#    BIND(?resource AS ?individual)
#    BIND(?class AS ?concept)''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} has a one of relationship with {{list}}, and {{resource}} is not in {{list}}, the assertion {{resource}} is a {{class}} leads to an inconsistency."# may need to revisit.. do we also check owl:differentFrom?
        ),
        "Data One Of" : autonomic.Deductor(
            reference = "Data One Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
        } #GROUP BY ?individual
    }
    FILTER(?dataCount=0)
#    BIND(?resource AS ?individual)
''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{datatypeProperty}} is restricted to have a value from {{list}}, and {{resource}} {{datatypeProperty}} {{value}}, but {{value}} is not in {{list}}, an inconsistency occurs."
        ), #need to come back to this
        #"Class Universal Quantification" (ObjectAllValuesFrom, DataAllValuesFrom)
        "Object All Values From" : autonomic.Deductor(
            reference = "Object All Values From",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?individual rdf:type ?class ; 
        ?objectProperty ?resource .
    ?objectProperty rdf:type owl:ObjectProperty .
    ?class rdfs:subClassOf|owl:equivalentClass
        [ rdf:type owl:Restriction;
            owl:onProperty ?objectProperty;
            owl:allValuesFrom ?valueclass ] .''',
            consequent = "?resource rdf:type ?valueclass.",
            explanation = "Since {{class}} has a restriction on {{objectProperty}} to have all values from {{valueclass}}, {{individual}} rdf:type {{class}}, and {{individual}} {{objectProperty}} {{resource}}, we can infer that {{resource}} rdf:type {{valueclass}}."
        ),
        "Data All Values From" : autonomic.Deductor(
            reference = "Data All Values From",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class ;
        ?datatypeProperty ?val .
    ?datatypeProperty rdf:type owl:DatatypeProperty .
    ?class rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Restriction ;
                owl:onProperty ?datatypeProperty ;
                owl:allValuesFrom ?value ] .
    FILTER(DATATYPE(?val)!= ?value)''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "{{resource}} {{datatypeProperty}} {{val}}, but {{val}} does not have the same datatype {{value}} restricted for {{datatypeProperty}} in {{class}}. Since {{resource}} rdf:type {{class}}, an inconsistency occurs."
        ),
        #"Cardinality Restriction" (ObjectMaxCardinality, ObjectMinCardinality, ObjectExactCardinality, DataMaxCardinality, DataMinCardinality, DataExactCardinality) 
        "Object Max Cardinality" : autonomic.Deductor(
            reference = "Object Max Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{objectProperty}} is assigned a maximum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ),# Still need to check distinctness of object
        "Object Min Cardinality" : autonomic.Deductor(#Works, but for lists of size greater than 1, additional (unnecessary) blank nodes are added. LIMIT 1 on the result would address this, but it is outside the where query
            reference = "Object Min Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource ?objectProperty [ rdf:type owl:Individual ] .",
            explanation = "Since {{objectProperty}} is assigned a minimum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is less than {{cardinalityValue}}, we can conclude the existence of additional assignments of {{objectProperty}} for {{resource}}."
        ),# Still need to check distinctness
#        "Object Exact Cardinality (Max)" : autonomic.Deductor(
#            reference = "Object Exact Cardinality (Max)",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
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
#            consequent = "?resource rdf:type owl:Nothing .",
#            explanation = "Since {{objectProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
#        ),# Still need to check distinctness of object
#        "Object Exact Cardinality (Min)" : autonomic.Deductor(#Works, but for lists of size greater than 1, additional (unnecessary) blank nodes are added. LIMIT 1 on the result would address this, but it is outside the where query
#            reference = "Object Exact Cardinality (Min)",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
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
#            consequent = "?resource ?objectProperty [ rdf:type owl:Individual ] .",
#            explanation = "Since {{objectProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{objectCount}} distinct assignments of {{objectProperty}} which is less than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
#        ),# Still need to check distinctness of object
        "Data Max Cardinality" : autonomic.Deductor(
            reference = "Data Max Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{dataProperty}} is assigned a maximum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ),
        "Data Min Cardinality" : autonomic.Deductor(
            reference = "Data Min Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource ?dataProperty [ rdf:type rdfs:Datatype ] .",
            explanation = "Since {{dataProperty}} is assigned a minimum cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is less than {{cardinalityValue}}, we can conclude the existence of additional assignments of {{dataProperty}} for {{resource}}."
        ),
        "Data Exact Cardinality" : autonomic.Deductor(
            reference = "Data Exact Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{dataProperty}} is assigned an exact cardinality of {{cardinalityValue}} for class {{class}}, {{resource}} rdf:type {{class}}, and {{resource}} has {{dataCount}} distinct assignments of {{dataProperty}} which is greater than {{cardinalityValue}}, we can conclude that there is an inconsistency associated with {{resource}}."
        ), # -- This is currently only accounting for max. Min accounted for in data min rule
        #"Disjunction" (ObjectUnionOf, DisjointUnion, and DataUnionOf)
        "Object Union Of" : autonomic.Deductor(
            reference = "Object Union Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type owl:Class ;
        rdfs:subClassOf|owl:equivalentClass
            [ rdf:type owl:Class ;
                owl:unionOf ?list ] .
    ?list rdf:rest*/rdf:first ?member .''',
            consequent = "?member rdfs:subClassOf ?resource .",
            explanation = "Since the class {{resource}} has a subclass or equivalent class relation with a class that comprises the union of {{list}}, which contains member {{member}}, we can infer that {{member}} is a subclass of {{resource}}."
        ),
        "Disjoint Union" : autonomic.Deductor(
            reference = "Disjoint Union",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?member rdfs:subClassOf ?resource ; owl:disjointWith ?item .",
            explanation = "Since the class {{resource}} has a subclass or equivalent class relation with a class that comprises the disjoint union of {{list}}, which contains member {{member}}, we can infer that {{member}} is a subclass of {{resource}} and disjoint with the other members of the list."
        ),
        "Data Union Of" : autonomic.Deductor(
            reference = "Data Union Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type ?class .",
            explanation = ""#add explanation here
        ),
        "Object Complement Of" : autonomic.Deductor(
            reference = "Object Complement Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?resource rdf:type ?class ,
            ?complementClass .
    ?class rdf:type owl:Class .
    ?complementClass rdf:type owl:Class .
    {?class owl:complementOf ?complementClass .} 
        UNION 
    {?complementClass owl:complementOf ?class .}''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} and {{complementClass}} are complementary, {{resource}} being of type both {{class}} and {{complementClass}} leads to an inconsistency."
        ),
        "Data Complement Of" : autonomic.Deductor(
            reference = "Data Complement Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?datatype rdf:type rdfs:Datatype ;
        owl:datatypeComplementOf ?complement .
    ?resource ?dataProperty ?value .
    ?dataProperty rdf:type owl:DatatypeProperty ;
        rdfs:range ?datatype .
    FILTER(DATATYPE(?value) = ?complement)''',
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{datatype}} is the complement of {{complement}}, {{dataProperty}} has range {{datatype}}, and {{resource}} {{dataProperty}} {{value}}, but {{value}} is of type {{complement}}, an inconsistency occurs."
        ),
        "Object Property Complement Of" : autonomic.Deductor(
            reference = "Object Property Complement Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} is a subclass of or is equivalent to a class with a complement restriction on the use of {{objectProperty}} to have values from {{restrictedClass}}, and {{resource}} is of type {{class}}, but has the link {{objectProperty}} to have values from an instance of {{restrictedClass}}, an inconsistency occurs." # do we also consider lists or complementary properties here?
        ),
        "Data Property Complement Of" : autonomic.Deductor(
            reference = "Data Property Complement Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{resource}} is a {{class}} which is equivalent to or a subclass of a class that has a complement of restriction on {{dataProperty}} to have some values from {{datatype}}, {{resource}} {{dataProperty}} {{value}}, but {{value}} has a datatype {{datatype}}, an inconsistency occurs."
        ),
        "Object Intersection Of" : autonomic.Deductor(
            reference = "Object Intersection Of",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type ?class.",
            explanation = "Since {{class}} is the intersection of the the members in {{list}}, and {{resource}} is of type each of the members in the list, then we can infer {{resource}} is a {{class}}."
        ),
#        "Data Intersection Of" : autonomic.Deductor(
#            reference = "Data Intersection Of",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
#    ?datatype rdf:type rdfs:Datatype ;
#        owl:intersectionOf ?list .
#    ?list rdf:rest*/rdf:first ?member .''',
#            consequent = "?resource rdf:type owl:Nothing .",
#            explanation = ""
#        ),
        "Object Qualified Max Cardinality" : autonomic.Deductor(
            reference = "Object Qualified Max Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} is constrained with a qualified max cardinality restriction on property {{objectProperty}} to have a max of {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}} which is more than {{value}}, we can infer that an inconsistency occurs."
        ),
        "Object Qualified Min Cardinality" : autonomic.Deductor(
            reference = "Object Qualified Min Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource ?objectProperty [ rdf:type owl:Individual ] .",
            explanation = "Since {{class}} is constrained with a qualified min cardinality restriction on property {{objectProperty}} to have a min of {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}} which is less than {{value}}, we can infer the existence of another object."
        ),
#        "Object Qualified Exact Cardinality (Max)" : autonomic.Deductor( # incorporated into object qualified min and max
#            reference = "Object Qualified Exact Cardinality (Max)",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
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
#            consequent = "?resource rdf:type owl:Nothing .",
#            explanation = "Since {{class}} is constrained with a qualified cardinality restriction on property {{objectProperty}} to have {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}}, an inconsistency occurs."
#        ),
#        "Object Qualified Exact Cardinality (Min)" : autonomic.Deductor(
#            reference = "Object Qualified Exact Cardinality (Min)",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
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
#            consequent = "?resource ?objectProperty [ rdf:type owl:Individual ] .",
#            explanation = "Since {{class}} is constrained with a qualified cardinality restriction on property {{objectProperty}} to have {{value}} objects of type class {{restrictedClass}}, and {{resource}} is a {{class}} but has {{objectCount}} objects assigned to {{objectProperty}} which is less than {{value}}, we can infer the existence of another object."
#        ),
#        "Data Qualified Max Cardinality" : autonomic.Deductor(#result shows up in blazegraph, but triple is not being added
#            reference = "Data Qualified Max Cardinality",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
#    ?resource ?datatypeProperty ?value .
#    ?datatypeProperty rdf:type owl:DatatypeProperty .
#    ?restriction rdf:type owl:Restriction ;
#        owl:onProperty ?datatypeProperty ;
#        owl:onDataRange ?datatype ;
#        owl:maxQualifiedCardinality|owl:qualifiedCardinality ?cardinalityValue .
#    {
#        SELECT (COUNT(DISTINCT ?value) AS ?valueCount) ?individual WHERE
#        {
#            ?individual ?datatypeProperty ?value .
#            ?datatypeProperty rdf:type owl:DatatypeProperty .
#            ?restriction rdf:type owl:Restriction ;
#                owl:onProperty ?datatypeProperty ;
#                owl:onDataRange ?datatype ;
#                owl:maxQualifiedCardinality|owl:qualifiedCardinality ?cardinalityValue .
#        } GROUP BY ?individual
#    }
#    BIND(?resource AS ?individual)
#    FILTER(DATATYPE(?value) = ?datatype)
#    FILTER(?valueCount > ?cardinalityValue)''',
#            consequent = "?resource rdf:type owl:Nothing .",
#            explanation = "Since {{datatypeProperty}} is constrained with a qualified max cardinality restriction on datatype {{datatype}} to have a max of {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, an inconsistency occurs."
#        ),
        "Data Qualified Max Cardinality" : autonomic.Deductor(
            reference = "Data Qualified Max Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{datatypeProperty}} is constrained with a qualified max cardinality restriction on datatype {{datatype}} to have a max of {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, an inconsistency occurs."
        ),
        "Data Qualified Min Cardinality" : autonomic.Deductor(
            reference = "Data Qualified Min Cardinality",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource ?datatypeProperty [ rdf:type rdfs:Datatype ] .",
            explanation = "Since {{datatypeProperty}} is constrained with a qualified min cardinality restriction on datatype {{datatype}} to have a min of {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, we can infer the existence of at least one more additional value."
        ),
#        "Data Qualified Exact Cardinality" : autonomic.Deductor(#result shows up in blazegraph, but triple is not being added
#            reference = "Data Qualified Exact Cardinality",
#            resource = "?resource", 
#            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
#            antecedent =  '''
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
#            consequent = "?resource rdf:type owl:Nothing .",
#            explanation = "Since {{datatypeProperty}} is constrained with a qualified cardinality restriction on datatype {{datatype}} to have {{cardinalityValue}} values, and {{resource}} has {{valueCount}} values of type {{datatype}} for property {{datatypeProperty}}, an inconsistency occurs."# currently the same as qualified max. need to incorporate min requirement
#        ),
        "Datatype Restriction" : autonomic.Deductor(
            reference = "Datatype Restriction",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?resource rdf:type owl:Nothing .",
            explanation = "Since {{class}} has a with restriction on datatype property {{dataProperty}} to be within the range specified in {{list}} with min value {{minValue}} and max value {{maxValue}}, and {{resource}} is of type {{class}} and has a value {{value}} for {{dataProperty}} which is outside the specified range, an inconsistency occurs."
        ),
        "All Disjoint Classes" : autonomic.Deductor(
            reference = "All Disjoint Classes",
            resource = "?restriction", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?member owl:disjointWith ?item .",
            explanation = "Since {{restriction}} is an all disjoint classes restriction with classes listed in {{list}}, each member in {{list}} is disjoint with each other member in the list."
        ),
        "All Disjoint Properties" : autonomic.Deductor(
            reference = "All Disjoint Properties",
            resource = "?restriction", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
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
            consequent = "?member owl:propertyDisjointWith ?item .",
            explanation = "Since {{restriction}} is an all disjoint properties restriction with properties listed in {{list}}, each member in {{list}} is disjoint with each other property in the list."
        ),
        "Object Property Chain Inclusion" : autonomic.Deductor(
            reference = "Object Property Chain Inclusion",
            resource = "?resource", 
            prefixes = {"owl": "http://www.w3.org/2002/07/owl#","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#"}, 
            antecedent =  '''
    ?objectProperty rdf:type owl:ObjectProperty ;
        owl:propertyChainAxiom ?list .
    ?list rdf:first ?prop1 .
    ?list rdf:rest/rdf:first ?prop2 .
    ?resource ?prop1 [ ?prop2 ?o ] .''',
            consequent = "?resource ?objectProperty ?o .",
            explanation = ""#currently limited to two properties
        ),
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
