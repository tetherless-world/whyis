# -*- config:utf-8 -*-

from whyis import importer
from whyis import autonomic
import logging

from datetime import datetime, timedelta

project_name = "whyis"

# Set to be custom for your project
LOD_PREFIX = 'http://purl.org/whyis/local'
#os.getenv('lod_prefix') if os.getenv('lod_prefix') else 'http://hbgd.tw.rpi.edu'

# from whyis.namespace import skos

class EmbeddedSystem:
    DEBUG = True  # we want debug level output
    # LOGGING
    LOGGER_NAME = "whyis_log"
    LOG_FILENAME = "log/output-whyis-%s.log" % (str(datetime.now()).replace(' ','_'))
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s" # used by logging.Formatter

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    EMBEDDED_FUSEKI = True

    EMBEDDED_CELERY = True
#    CELERYD_CONCURRENCY = 4
    CELERY_DISABLE_ALL_RATE_LIMITS = True

    DEFAULT_ANONYMOUS_READ = True

    NANOPUB_ARCHIVE = {
        'depot.storage_path' : "nanopublications",
    }
    FILE_ARCHIVE = {
        'cache_max_age' : 3600*24*7,
        'depot.storage_path' : 'files'
    }

    CACHE_TYPE = "simple" # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 0


    # see example/ for reference
    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = []

# base config class; extend it to your needs.
class Config:
    # use DEBUG mode?
    DEBUG = True

    SITE_NAME = "Whyis"

    BASE_RATE_PROBABILITY = 0.6

    # use TESTING mode?
    TESTING = False

    #JS CONFIG - VUE JS
    ##USE CUSTOM REST BACKUP & RESTORE
    THIRD_PARTY_REST_BACKUP = False
    DISABLE_VUE_SPEED_DIAL = True

    # use server x-sendfile?
    USE_X_SENDFILE = False

    WTF_CSRF_ENABLED = True
    SECRET_KEY = "secret"  # import os; os.urandom(24)

    DELETE_ARCHIVE_NANOPUBS = False

    WHYIS_TEMPLATE_DIR = None
    WHYIS_CDN_DIR = None

    DEFAULT_ANONYMOUS_READ = True

    SITE_HEADER_IMAGE = '/static/images/random_network.png'

    LOD_PREFIX = LOD_PREFIX
    DEFAULT_LANGUAGE = 'en'

    MULTIUSER = True

    PLUGINENGINE_NAMESPACE = "whyis"
    PLUGINENGINE_PLUGINS = ['whyis_sparql_entity_resolver']

    SECURITY_EMAIL_SENDER = "Name <email@example.com>"
    SECURITY_FLASH_MESSAGES = True
    SECURITY_CONFIRMABLE = False
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_REGISTER_URL = '/register'
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = 'changeme__'
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_POST_LOGIN_VIEW = "/"
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_DEFAULT_REMEMBER_ME = True
    ADMIN_EMAIL_RECIPIENTS = []
    LOGIN_USER_TEMPLATE = "auth/login.html"

    WHYIS_TEMPLATE_DIR = [
        "templates",
    ]

    NAMESPACES = [
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
        )
#        importer.LinkedData(
#            prefix = LOD_PREFIX+'/dbpedia/class/',
#            url = 'http://dbpedia.org/class/%s',
#            access_url = 'http://dbpedia.org/sparql?default-graph-uri=http://dbpedia.org&query=DESCRIBE+<%s>&format=application/json-ld',
#            format='json-ld',
#        )
    ]
    INFERENCERS = dict(
        SETLr = autonomic.SETLr(),
# include a reasoning profile by inlining the dictionary
#        ** reasoning_profiles.all
#        HTML2Text = nlp.HTML2Text(),
#        EntityExtractor = nlp.EntityExtractor(),
#        EntityResolver = nlp.EntityResolver(),
#        TF-IDFCalculator = nlp.TFIDFCalculator(),
#        SKOSCrawler = autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related])
    )
    INFERENCE_TASKS = [
#        dict ( name="SKOS Crawler",
#               service=autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related]),
#               schedule=dict(hour="1")
#              )
    ]



# config class for development environment
class Dev(Config):
    DEBUG = True  # we want debug level output
    MAIL_DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    WTF_CSRF_ENABLED = False


# config class used during tests
class Test(Config):
    DEBUG=False
    NANOPUB_ARCHIVE = {
        'depot.backend' : 'depot.io.memory.MemoryFileStorage'
    }

    DEFAULT_ANONYMOUS_READ = False
    FILE_ARCHIVE = {
        'depot.backend' : 'depot.io.memory.MemoryFileStorage'
    }
    TESTING = True
    WTF_CSRF_ENABLED = False
