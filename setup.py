import os
from distutils.core import setup
import distutils.command.build_ext
import requests
import subprocess

from os import path as osp
from fnmatch import fnmatch


def package_data_with_recursive_dirs(package_data_spec):
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
                        if not pattern or fnmatch(filename, pattern):
                            relname = osp.normpath(osp.join(datadir, osp.relpath(filename, directory)))
                            out_entries.append(relname)
            else:  # datadir is not really a datadir but a glob or something else
                out_entries.append(datadir)  # we just copy the entry
        out_spec[package_name] = out_entries
    return out_spec


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def build_js():
    subprocess.run('npm install',shell=True,cwd='whyis/static')
    subprocess.run('npm run build',shell=True,cwd='whyis/static')


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
        print('Building JavaScript...')
        build_js()
        print('Downloading Fuseki Jars...')
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
#        'Click',
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
    package_data=package_data_with_recursive_dirs({
        'whyis.fuseki': ['jars/*.jar','webapp'],
        'whyis': ['config-template','static','templates']
    }),
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
