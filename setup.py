import os
from distutils.core import setup
import distutils.command.build_ext
import requests
import subprocess

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def build_js():
    subprocess.run('npm install'.split(' '),shell=True,cwd='static')

def download_file(url, filename=None):
    filename = url.split('/')[-1] if filename is None else filename
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
    return filename

def download_files():
    files = {
        'whyis/fuseki/jars/fuseki-server.jar' : 'https://search.maven.org/remotecontent?filepath=org/apache/jena/jena-fuseki-fulljar/3.17.0/jena-fuseki-fulljar-3.17.0.jar',
#        'whyis/fuseki/jars/jena-spatial.jar': 'https://repo1.maven.org/maven2/org/apache/jena/jena-spatial/3.12.0/jena-spatial-3.12.0.jar'
# TODO: https://jena.apache.org/documentation/query/spatial-query.html#spatial-dataset-assembler
    }
    for dest, url in files.items():
        print("Downloading %s..." % dest)
        download_file(url, dest)
    print("Downloads complete.")

class BuildExtCommand(distutils.command.build_ext.build_ext):
    """Custom build command."""

    def run(self):
        download_files()
        distutils.command.build_ext.build_ext.run(self)


# mvn -q clean compile assembly:single -PwhyisProfile

setup(
    name = "whyis",
    version = "2.0",
    author = "Jamie McCusker",
    author_email = "mccusj@cs.rpi.edu",
    description = ("Whyis is a nano-scale knowledge graph publishing, management, and analysis framework."),
    license = "Apache License 2.0",
    keywords = "rdf semantic knowledge graph",
    url = "http://packages.python.org/whyis",
    packages=['whyis'],
    long_description='''Whyis is a nano-scale knowledge graph publishing,
    management, and analysis framework. Whyis aims to support domain-aware management
    and curation of knowledge from many different sources. Its primary goal is to enable
    creation of useful domain- and data-driven knowledge graphs. Knowledge can be
    contributed and managed through direct user interaction, statistical analysis,
    or data ingestion from many different kinds of data sources. Every contribution to
    the knowledge graph is managed as a separate entity so that its provenance
    (publication status, attribution, and justification) is transparent and can
    be managed and used.''',
    include_package_data = True,
    cmdclass={
        'build_ext': BuildExtCommand,
    },
    setup_requires = [
        'wheel',
        'requests'
    ],
    install_requires = [
#        'amqp==2.5.1',
#        'arrow==0.14.2',
#        'asn1crypto==0.24.0',
#        'Babel==2.7.0',
#        'bcrypt==3.1.6',
        'beautifulsoup4==4.7.1',
        'bibtexparser==1.1.0',
#        'billiard==3.6.1.0',
#        'binaryornot==0.4.4',
#        'blinker==1.4',
        'bsddb3==6.2.6',
        'celery',
        'celery_once',
#        'certifi==2019.3.9',
#        'cffi==1.12.3',
#        'chardet==3.0.4',
        'Click',
        'cookiecutter',
#        'cryptography==',
#        'Cython==0.29.10',
#        'fabric==2.4.0',
        'email_validator',
        'filedepot',
        'Flask',
        'Flask-Login',
        'Flask-Script',
        'Flask-Security',
        'Flask-WTF',
        'html5lib',
#        'idna==2.8',
        'ijson==2.4',
#        'invoke==1.2.0',
#        'isodate==0.6.0',
#        'itsdangerous==1.1.0',
        'Jinja2',
        'jinja2-time',
        'keepalive',
        'lxml',
        'Markdown',
#        'MarkupSafe==1.1.1',
        'nltk',
        'nose',
        'numpy',
        'pandas',
#        'paramiko==2.5.0',
#        'passlib==1.7.1',
#        'poyo==0.4.2',
#        'pycparser==2.19',
#        'pygeoif==0.7',
        'PyJWT',
#        'PyNaCl==1.3.0',
#        'pyOpenSSL==19.0.0',
        'pyparsing',
        'pyshp',
        'python-dateutil',
        'python-magic',
        'python-slugify',
#        'pytidylib==0.3.2',
#        'pytz==2019.1',
        'rdflib',
        'rdflib-jsonld',
#        'redis==3.3.8',
        'requests[security]',
#        'requests-testadapter==0.3.0',
        'sadi',
        'scipy',
        'setlr==0.2.14',
        'sdd2rdf',
#        'six==1.12.0',
#        'soupsieve==1.9.1',
#        'SPARQLWrapper==1.8.4',
#        'speaklater==1.3',
#        'text-unidecode==1.2',
#        'toposort==1.5',
#        'urllib3==1.25.3',
#        'vine==1.3.0',
#        'virtualenv==16.6.0',
#        'webencodings==0.5.1',
#        'WebOb==1.8.5',
#        'Werkzeug==0.15.3',
#        'whichcraft==0.5.2',
#        'WTForms==2.2.1',
        'xlrd',
        'Flask-Caching'
    ],
    tests_require=[
        'pytest-flask',
        'coverage==4.5.3',
        'flask-testing',
        'unittest-xml-reporting==2.5.1'
    ],
    package_data={
        'whyis.fuseki': ['jars/*.jar','webapp/*'],
        'whyis': ['config-template/*']
    },
    entry_points = {
        'console_scripts': [
            'whyis=whyis.manager:main',
            'fuseki-server=whyis.fuseki:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "License :: OSI Approved :: Apache Software License",
    ],
)
