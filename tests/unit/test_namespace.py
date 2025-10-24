"""
Unit tests for whyis.namespace module.

Tests the namespace container and namespace definitions.
"""

import pytest
from rdflib import Namespace, URIRef
from whyis.namespace import NS, NamespaceContainer


class TestNamespaceContainer:
    """Test the NamespaceContainer class."""
    
    def test_namespace_container_has_rdf(self):
        """Test that NS has RDF namespace."""
        assert hasattr(NS, 'RDF')
        assert hasattr(NS, 'rdf')
    
    def test_namespace_container_has_rdfs(self):
        """Test that NS has RDFS namespace."""
        assert hasattr(NS, 'RDFS')
        assert hasattr(NS, 'rdfs')
    
    def test_namespace_container_has_owl(self):
        """Test that NS has OWL namespace."""
        assert hasattr(NS, 'owl')
        assert isinstance(NS.owl, Namespace)
    
    def test_namespace_container_has_foaf(self):
        """Test that NS has FOAF namespace."""
        assert hasattr(NS, 'foaf')
        assert isinstance(NS.foaf, Namespace)
    
    def test_namespace_container_has_dc(self):
        """Test that NS has Dublin Core namespace."""
        assert hasattr(NS, 'dc')
        assert hasattr(NS, 'dcterms')
        assert isinstance(NS.dc, Namespace)
    
    def test_namespace_container_has_prov(self):
        """Test that NS has PROV namespace."""
        assert hasattr(NS, 'prov')
        assert isinstance(NS.prov, Namespace)
    
    def test_namespace_container_has_skos(self):
        """Test that NS has SKOS namespace."""
        assert hasattr(NS, 'skos')
        assert isinstance(NS.skos, Namespace)
    
    def test_namespace_container_has_whyis(self):
        """Test that NS has Whyis namespace."""
        assert hasattr(NS, 'whyis')
        assert isinstance(NS.whyis, Namespace)
    
    def test_namespace_container_has_np(self):
        """Test that NS has nanopub namespace."""
        assert hasattr(NS, 'np')
        assert isinstance(NS.np, Namespace)
    
    def test_namespace_container_has_sio(self):
        """Test that NS has SIO namespace."""
        assert hasattr(NS, 'sio')
        assert isinstance(NS.sio, Namespace)
    
    def test_namespace_container_has_setl(self):
        """Test that NS has SETL namespace."""
        assert hasattr(NS, 'setl')
        assert isinstance(NS.setl, Namespace)
    
    def test_namespace_container_has_sdd(self):
        """Test that NS has SDD namespace."""
        assert hasattr(NS, 'sdd')
        assert isinstance(NS.sdd, Namespace)
    
    def test_namespace_prefixes_property(self):
        """Test that prefixes property returns a dictionary."""
        prefixes = NS.prefixes
        assert isinstance(prefixes, dict)
        assert len(prefixes) > 0
    
    def test_namespace_prefixes_contains_rdf(self):
        """Test that prefixes contains RDF."""
        prefixes = NS.prefixes
        assert 'rdf' in prefixes or 'RDF' in prefixes
    
    def test_namespace_prefixes_contains_rdfs(self):
        """Test that prefixes contains RDFS."""
        prefixes = NS.prefixes
        assert 'rdfs' in prefixes or 'RDFS' in prefixes
    
    def test_namespace_prefixes_values_are_namespaces(self):
        """Test that all prefix values are Namespace instances."""
        prefixes = NS.prefixes
        for key, value in prefixes.items():
            assert isinstance(value, Namespace), f"Prefix {key} is not a Namespace"
    
    def test_namespace_rdf_type(self):
        """Test that we can create URIRefs from namespaces."""
        rdf_type = NS.RDF.type
        assert isinstance(rdf_type, URIRef)
        assert str(rdf_type) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    
    def test_namespace_owl_class(self):
        """Test OWL Class URI."""
        owl_class = NS.owl.Class
        assert isinstance(owl_class, URIRef)
        assert str(owl_class) == 'http://www.w3.org/2002/07/owl#Class'
    
    def test_namespace_foaf_person(self):
        """Test FOAF Person URI."""
        foaf_person = NS.foaf.Person
        assert isinstance(foaf_person, URIRef)
        assert str(foaf_person) == 'http://xmlns.com/foaf/0.1/Person'
    
    def test_namespace_container_instantiation(self):
        """Test that NamespaceContainer can be instantiated."""
        container = NamespaceContainer()
        assert hasattr(container, 'RDF')
        assert hasattr(container, 'RDFS')
        assert hasattr(container, 'prefixes')
    
    def test_namespace_schema_org(self):
        """Test Schema.org namespace."""
        assert hasattr(NS, 'schema')
        assert isinstance(NS.schema, Namespace)
    
    def test_namespace_dcat(self):
        """Test DCAT namespace."""
        assert hasattr(NS, 'dcat')
        assert isinstance(NS.dcat, Namespace)
    
    def test_namespace_csvw(self):
        """Test CSVW namespace."""
        assert hasattr(NS, 'csvw')
        assert isinstance(NS.csvw, Namespace)
    
    def test_namespace_void(self):
        """Test VoID namespace."""
        assert hasattr(NS, 'void')
        assert isinstance(NS.void, Namespace)
    
    def test_namespace_text(self):
        """Test Jena text namespace."""
        assert hasattr(NS, 'text')
        assert isinstance(NS.text, Namespace)


class TestNamespaceURIs:
    """Test specific namespace URIs are correct."""
    
    def test_rdf_namespace_uri(self):
        """Test RDF namespace URI."""
        assert str(NS.rdf) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    
    def test_rdfs_namespace_uri(self):
        """Test RDFS namespace URI."""
        assert str(NS.rdfs) == 'http://www.w3.org/2000/01/rdf-schema#'
    
    def test_owl_namespace_uri(self):
        """Test OWL namespace URI."""
        assert str(NS.owl) == 'http://www.w3.org/2002/07/owl#'
    
    def test_foaf_namespace_uri(self):
        """Test FOAF namespace URI."""
        assert str(NS.foaf) == 'http://xmlns.com/foaf/0.1/'
    
    def test_dc_namespace_uri(self):
        """Test Dublin Core namespace URI."""
        assert str(NS.dc) == 'http://purl.org/dc/terms/'
    
    def test_prov_namespace_uri(self):
        """Test PROV namespace URI."""
        assert str(NS.prov) == 'http://www.w3.org/ns/prov#'
    
    def test_whyis_namespace_uri(self):
        """Test Whyis namespace URI."""
        assert str(NS.whyis) == 'http://vocab.rpi.edu/whyis/'
    
    def test_np_namespace_uri(self):
        """Test nanopub namespace URI."""
        assert str(NS.np) == 'http://www.nanopub.org/nschema#'
    
    def test_sio_namespace_uri(self):
        """Test SIO namespace URI."""
        assert str(NS.sio) == 'http://semanticscience.org/resource/'
    
    def test_setl_namespace_uri(self):
        """Test SETL namespace URI."""
        assert str(NS.setl) == 'http://purl.org/twc/vocab/setl/'
    
    def test_schema_namespace_uri(self):
        """Test Schema.org namespace URI."""
        assert str(NS.schema) == 'http://schema.org/'
