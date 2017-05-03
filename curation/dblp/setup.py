import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "setlr",
    version = "0.1.5",
    author = "Jim McCusker",
    author_email = "mccusj@cs.rpi.edu",
    description = ("setlr is a tool for Semantic Extraction, Transformation, and Loading."),
    license = "Apache License 2.0",
    keywords = "rdf semantic etl",
    url = "http://packages.python.org/setlr",
#    packages=['setlr'],
    long_description='''SETLr is a tool for generating RDF graphs, including named graphs, from almost any kind of tabular data.''',
    include_package_data = True,
    install_requires = [
        'rdflib',
        'rdflib-jsonld',
        'pandas',
        'requests',
        'toposort',
        'beautifulsoup4',
        'jinja2',
        'lxml',
        'xlrd',
        'ijson',
        'requests-testadapter',
        'python-slugify',
    ],
    entry_points = {
        'console_scripts': ['setlr=setlr:main'],
    },
    packages = find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)
