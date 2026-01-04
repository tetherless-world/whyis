"""
Unit tests for package compatibility after upgrade.

Tests that upgraded packages can be imported and basic functionality works.
"""

import pytest


class TestFlaskEcosystem:
    """Test Flask and related packages."""
    
    def test_flask_import(self):
        """Test that Flask can be imported."""
        import flask
        assert hasattr(flask, '__version__')
        # Flask 3.x should be installed (accepting 2.x+ for forward compatibility)
        major_version = int(flask.__version__.split('.')[0])
        assert major_version >= 3, "Flask should be version 3.x or higher"
    
    def test_flask_basics(self):
        """Test basic Flask functionality."""
        from flask import Flask
        app = Flask(__name__)
        assert app is not None
        assert app.name == __name__
    
    def test_jinja2_import(self):
        """Test that Jinja2 can be imported."""
        import jinja2
        assert hasattr(jinja2, '__version__')
        # Jinja2 3.x should be installed
        major_version = int(jinja2.__version__.split('.')[0])
        assert major_version >= 3, "Jinja2 should be version 3.x"
    
    def test_werkzeug_import(self):
        """Test that Werkzeug can be imported."""
        import werkzeug
        # Werkzeug 3.x may not expose __version__ at top level
        # Just verify we can import and use it
        from werkzeug.utils import secure_filename
        assert secure_filename is not None
    
    def test_itsdangerous_import(self):
        """Test that itsdangerous can be imported."""
        import itsdangerous
        assert hasattr(itsdangerous, '__version__')
        # Should be 2.x
        major_version = int(itsdangerous.__version__.split('.')[0])
        assert major_version >= 2, "itsdangerous should be version 2.x"
    
    def test_markupsafe_import(self):
        """Test that markupsafe can be imported."""
        import markupsafe
        assert hasattr(markupsafe, '__version__')


class TestFlaskExtensions:
    """Test Flask extensions."""
    
    def test_flask_security_too_import(self):
        """Test that Flask-Security-Too can be imported as flask_security."""
        import flask_security
        assert flask_security is not None
        # Should have Security class
        assert hasattr(flask_security, 'Security')
    
    def test_flask_login_import(self):
        """Test that Flask-Login can be imported."""
        import flask_login
        assert hasattr(flask_login, '__version__')
    
    def test_flask_wtf_import(self):
        """Test that Flask-WTF can be imported."""
        import flask_wtf
        assert hasattr(flask_wtf, '__version__')
    
    def test_flask_caching_import(self):
        """Test that Flask-Caching can be imported."""
        import flask_caching
        assert flask_caching is not None
    
    def test_flask_script_import(self):
        """Test that Flask-Script can be imported with Flask 3.x compatibility patch."""
        import sys
        import types
        
        # Apply Flask 3.x compatibility patches for Flask-Script
        # Patch 1: Create flask._compat module (removed in Flask 3.x)
        if 'flask._compat' not in sys.modules:
            compat_module = types.ModuleType('flask._compat')
            compat_module.text_type = str
            compat_module.string_types = (str,)
            sys.modules['flask._compat'] = compat_module
        
        # Patch 2: Add _request_ctx_stack if missing (removed in Flask 3.x)
        import flask
        if not hasattr(flask, '_request_ctx_stack'):
            from werkzeug.local import LocalStack
            flask._request_ctx_stack = LocalStack()
        
        # Patch 3: Add _app_ctx_stack if missing (removed in Flask 3.x)
        if not hasattr(flask, '_app_ctx_stack'):
            from werkzeug.local import LocalStack
            flask._app_ctx_stack = LocalStack()
        
        # Now import should work
        import flask_script
        assert flask_script is not None
        assert hasattr(flask_script, 'Manager')


class TestRDFPackages:
    """Test RDF and semantic web packages."""
    
    def test_rdflib_import(self):
        """Test that rdflib can be imported."""
        import rdflib
        assert hasattr(rdflib, '__version__')
        # Should be rdflib 7.x
        major_version = int(rdflib.__version__.split('.')[0])
        assert major_version >= 6, "rdflib should be version 6.x or 7.x"
    
    def test_rdflib_basics(self):
        """Test basic rdflib functionality."""
        from rdflib import Graph, Literal, Namespace, URIRef, RDF
        
        # Create a graph
        g = Graph()
        
        # Add a triple
        ex = Namespace("http://example.org/")
        g.add((ex.subject, RDF.type, ex.Thing))
        g.add((ex.subject, ex.predicate, Literal("object")))
        
        # Query
        assert len(g) == 2
        assert (ex.subject, RDF.type, ex.Thing) in g
    
    def test_rdflib_jsonld_import(self):
        """Test that rdflib-jsonld can be imported."""
        import rdflib_jsonld
        assert rdflib_jsonld is not None
    
    def test_oxrdflib_import(self):
        """Test that oxrdflib can be imported."""
        import oxrdflib
        assert oxrdflib is not None


class TestDataProcessing:
    """Test data processing packages."""
    
    def test_beautifulsoup4_import(self):
        """Test that BeautifulSoup can be imported."""
        from bs4 import BeautifulSoup
        assert BeautifulSoup is not None
    
    def test_beautifulsoup4_basics(self):
        """Test basic BeautifulSoup functionality."""
        from bs4 import BeautifulSoup
        html = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        assert soup.find('p').text == 'Test'
    
    def test_lxml_import(self):
        """Test that lxml can be imported."""
        import lxml
        assert lxml is not None
        from lxml import etree
        assert etree is not None
    
    def test_pandas_import(self):
        """Test that pandas can be imported."""
        import pandas as pd
        assert hasattr(pd, '__version__')
    
    def test_numpy_import(self):
        """Test that numpy can be imported."""
        import numpy as np
        assert hasattr(np, '__version__')
    
    def test_scipy_import(self):
        """Test that scipy can be imported."""
        import scipy
        assert hasattr(scipy, '__version__')


class TestUtilityPackages:
    """Test utility packages."""
    
    def test_celery_import(self):
        """Test that celery can be imported."""
        import celery
        assert hasattr(celery, '__version__')
        # Should be celery 5.x
        major_version = int(celery.__version__.split('.')[0])
        assert major_version >= 5, "celery should be version 5.x"
    
    def test_eventlet_import(self):
        """Test that eventlet can be imported."""
        import eventlet
        assert hasattr(eventlet, '__version__')
    
    def test_dnspython_import(self):
        """Test that dnspython can be imported."""
        import dns
        assert dns is not None
    
    def test_requests_import(self):
        """Test that requests can be imported."""
        import requests
        assert hasattr(requests, '__version__')
    
    def test_nltk_import(self):
        """Test that nltk can be imported."""
        import nltk
        assert hasattr(nltk, '__version__')
    
    def test_markdown_import(self):
        """Test that Markdown can be imported."""
        import markdown
        assert hasattr(markdown, '__version__')
    
    def test_markdown_basics(self):
        """Test basic Markdown functionality."""
        import markdown
        html = markdown.markdown("# Test")
        assert "<h1>" in html
        assert "Test" in html


class TestWhyisCompatibility:
    """Test Whyis-specific compatibility."""
    
    def test_whyis_import(self):
        """Test that whyis can be imported."""
        import whyis
        assert whyis is not None
    
    def test_whyis_namespace_import(self):
        """Test that whyis.namespace can be imported."""
        from whyis.namespace import NS
        assert NS is not None
        assert hasattr(NS, 'RDF')
        assert hasattr(NS, 'RDFS')
    
    def test_whyis_namespace_with_rdflib(self):
        """Test that whyis namespace works with upgraded rdflib."""
        from whyis.namespace import NS
        from rdflib import Graph, URIRef
        
        g = Graph()
        # Test namespace usage
        assert isinstance(NS.RDF.type, URIRef)
        assert isinstance(NS.owl.Class, URIRef)
        
        # Test adding to graph
        ex_subject = URIRef("http://example.org/subject")
        g.add((ex_subject, NS.RDF.type, NS.owl.Class))
        assert len(g) == 1
    
    def test_flask_security_mixins(self):
        """Test that Flask-Security mixins can be imported."""
        from flask_security import UserMixin, RoleMixin
        assert UserMixin is not None
        assert RoleMixin is not None
    
    def test_flask_security_security_class(self):
        """Test that Flask-Security Security class works."""
        from flask_security import Security
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['SECURITY_PASSWORD_SALT'] = 'test-salt'
        
        # Security should be instantiable
        security = Security()
        assert security is not None
