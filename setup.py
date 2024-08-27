import os
from distutils.core import setup
import distutils.command.build
import distutils.command.sdist
import subprocess

from os import path as osp
from fnmatch import fnmatch

from whyis._version import __version__

def package_data_with_recursive_dirs(package_data_spec, exclude=[]):
    """converts modified package_data dict to a classic package_data dict
    Where normal package_data entries can only specify globs, the
    modified package_data dict can have
       a) directory names or
       b) tuples of a directory name and a pattern
    as entries in addition to normal globs.
    When one of a) or b) is encountered, the entry is expanded so
    that the resulting package_data contains all files (optionally
    filtered by pattern) encountered by recursively searching the
    directory.

    Usage:
    setup(
    ...
        package_data = package_data_with_recursive_dirs({
            'module': ['dir1', ('dir2', '*.xyz')],
            'module2': ['dir3/file1.txt']
                })
    )
    """
    out_spec = {}
    for package_name, spec in package_data_spec.items():
        # replace dots by operating system path separator
        package_path = osp.join(*package_name.split('.'))
        out_entries = []
        for entry in spec:
            directory = None  # full path to data dir
            pattern = None  # pattern to append
            datadir = None  # data dir relative to package (as specified)
            try:  # entry is just a string
                directory = osp.join(package_path, entry)
                datadir = entry
                pattern = None
            except (TypeError, AttributeError):  # entry has additional pattern spec
                directory = osp.join(package_path, entry[0])
                pattern = entry[1]
                datadir = entry[0]
            if osp.isdir(directory):  # only apply if it is really a directory
                for (dirpath, dirnames, filenames) in os.walk(directory):
                    for filename in (osp.join(dirpath, f) for f in filenames):
                        filename_parts = set(filename.split(os.path.sep))
                        for ex in exclude:
                            if ex in filename_parts:
                                continue
                        if not pattern or fnmatch(filename, pattern):
                            relname = osp.normpath(osp.join(datadir, osp.relpath(filename, directory)))
                            out_entries.append(relname)
            else:  # datadir is not really a datadir but a glob or something else
                out_entries.append(datadir)  # we just copy the entry
        out_spec[package_name] = out_entries
    print(out_spec)
    return out_spec


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def build_js():
    subprocess.run('npm install',shell=True,cwd='whyis/static')
    subprocess.run('npm run build-dev',shell=True,cwd='whyis/static')


def download_file(url, filename=None):
    import requests
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
        'whyis/fuseki/jars/fuseki-server.jar' : 'https://search.maven.org/remotecontent?filepath=org/apache/jena/jena-fuseki-fulljar/4.3.2/jena-fuseki-fulljar-4.3.2.jar',
#        'whyis/fuseki/jars/jena-spatial.jar': 'https://repo1.maven.org/maven2/org/apache/jena/jena-spatial/3.12.0/jena-spatial-3.12.0.jar'
# TODO: https://jena.apache.org/documentation/query/spatial-query.html#spatial-dataset-assembler
    }
    for dest, url in files.items():
        print("Downloading %s..." % dest)
        download_file(url, dest)
    print("Downloads complete.")

class BuildCommand(distutils.command.build.build):
    """Custom build command."""

    def run(self):
        print('boo')
        if os.path.exists('.git'): # build these if we are building from repo
            print('Building JavaScript...')
            build_js()
            print('Downloading Fuseki Jars...')
            download_files()
        distutils.command.build.build.run(self)

class SdistCommand(distutils.command.sdist.sdist):
    """Custom sdist command."""

    def run(self):
        print('Building JavaScript...')
        build_js()
        print('Downloading Fuseki Jars...')
        download_files()
        distutils.command.sdist.sdist.run(self)


# mvn -q clean compile assembly:single -PwhyisProfile

setup(
    name = "whyis",
    version = __version__,
    author = "Jamie McCusker",
    author_email = "mccusj@cs.rpi.edu",
    description = ("Whyis is a nano-scale knowledge graph publishing, management, and analysis framework."),
    license = "Apache License 2.0",
    keywords = "rdf semantic knowledge graph",
    url = "http://tetherless-world.github.io/whyis",
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
    cmdclass={
        'build': BuildCommand,
#        'sdist': SdistCommand,
    },
    setup_requires = [
        'wheel',
        'requests'
    ],
    install_requires = [
        'beautifulsoup4==4.7.1',
        'bibtexparser==1.1.0',
        'celery<6.0.0',
        'celery_once==3.0.1',
        'cookiecutter==1.7.3',
        'email_validator==1.1.3',
        'eventlet==0.33.0',
        'dnspython==2.2.1',
        'filedepot==0.10.0',
        # Upgrade to 2.0 when Celery can use click 8.0
        'Flask<2.0',
        'Flask-Login==0.5.0',
        'Flask-Script==2.0.6',
        'Flask-Security==3.0.0',
        'itsdangerous<2.0,>=0.24',
        'Flask-PluginEngine==0.5',
        # remove version when upgrading to Flask 2.0
        'Flask-WTF<0.15',
        'html5lib==1.1',
        'ijson==2.4',
        'itsdangerous<2.0,>=0.24',
        'jinja2-time',
        'Jinja2==2.11.3',
        #'keepalive',
        'lxml',
        'Markdown',
        'markupsafe==2.0.1',
        #'mod-wsgi==4.9.0',
        'nltk==3.6.5',
        'nose',
        'numpy',
        'oxrdflib==0.3.1',
        'pandas',
        'PyJWT',
        'pyparsing',
        'pyshp',
        'python-dateutil',
        'puremagic==1.14',
        'python-slugify',
        'rdflib==6.3.2',
        'rdflib-jsonld==0.6.2',
        'redislite>=6',
        'requests[security]',
        'sadi',
        'scipy',
        'setlr>=1.0.1',
        'sdd2rdf>=1.1.0',
        'xlrd==2.0.1',
        'werkzeug==2.0.3',
        'Flask-Caching==1.10.1'
    ],
    tests_require=[
        'pytest-flask',
        'coverage==4.5.3',
        'flask-testing',
        'unittest-xml-reporting==2.5.1'
    ],
    python_requires='>=3.7',
    include_package_data=True,
    # package_data=package_data_with_recursive_dirs({
    #     'whyis.fuseki': ['jars/*.jar','webapp'],
    #     'whyis': [
    #         'config-template',
    #         'static',
    #         'templates'
    #     ]
    # }, exclude=['node_modules']),
    entry_points = {
        'console_scripts': [
            'whyis=whyis.manager:main',
            'fuseki-server=whyis.fuseki:main',
        ],
        'rdf.plugins.resultparser' : [
            'text/turtle = rdflib.plugins.sparql.results.graph:GraphResultParser'
        ],
        'whyis': [
         'whyis_sparql_entity_resolver = whyis.plugins.sparql_entity_resolver:SPARQLEntityResolverPlugin',
         'whyis_knowledge_explorer = whyis.plugins.knowledge_explorer:KnowledgeExplorerPlugin'
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "License :: OSI Approved :: Apache Software License",
    ],
)
