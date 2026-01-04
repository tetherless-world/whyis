# -*- coding:utf-8 -*-

"""
AWS Neptune SPARQL Store with IAM Authentication.

This module provides SPARQL store implementations that support AWS IAM authentication
for Amazon Neptune databases using SigV4 request signing.
"""

import re
from rdflib.plugins.stores.sparqlconnector import SPARQLConnector, Result
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from requests_aws4auth import AWS4Auth
import boto3
import requests
from io import BytesIO
from urllib.parse import urlencode
from typing import Optional


class NeptuneSPARQLConnector(SPARQLConnector):
    """
    SPARQL Connector that uses AWS SigV4 authentication for Neptune.
    
    This connector replaces the standard urlopen-based connector with
    a requests-based implementation that supports AWS IAM authentication.
    """
    
    def __init__(self, *args, region_name=None, service_name='neptune-db', **kwargs):
        """
        Initialize Neptune SPARQL Connector.
        
        Args:
            region_name: AWS region where Neptune instance is located
            service_name: AWS service name for signing (default: 'neptune-db')
            *args, **kwargs: Additional arguments passed to SPARQLConnector
        """
        super().__init__(*args, **kwargs)
        self.region_name = region_name
        self.service_name = service_name
        self._aws_auth = None
        self._session = None
        
    def _get_session(self):
        """
        Get or create requests session with AWS authentication.
        
        Returns:
            requests.Session configured with AWS4Auth
        """
        if self._session is None:
            self._session = requests.Session()
            # Get AWS credentials from the environment/IAM role
            credentials = boto3.Session().get_credentials()
            self._aws_auth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                self.region_name,
                self.service_name,
                session_token=credentials.token
            )
            self._session.auth = self._aws_auth
        return self._session
    
    def query(self, query: str, default_graph: Optional[str] = None, 
              named_graph: Optional[str] = None) -> Result:
        """
        Execute SPARQL query with AWS IAM authentication.
        
        Args:
            query: SPARQL query string
            default_graph: Default graph URI
            named_graph: Named graph URI
            
        Returns:
            Query results
        """
        if not self.query_endpoint:
            raise Exception("Query endpoint not set!")
            
        session = self._get_session()
        params = {}
        
        if default_graph is not None:
            params["default-graph-uri"] = default_graph
            
        headers = {"Accept": self.response_mime_types()}
        
        if self.method == "GET":
            params["query"] = query
            response = session.get(self.query_endpoint, params=params, headers=headers)
        elif self.method == "POST":
            headers.update({"Content-Type": "application/sparql-query"})
            response = session.post(self.query_endpoint, params=params, 
                                   data=query.encode('utf-8'), headers=headers)
        elif self.method == "POST_FORM":
            params["query"] = query
            headers.update({"Content-Type": "application/x-www-form-urlencoded"})
            response = session.post(self.query_endpoint, 
                                   data=urlencode(params).encode('utf-8'), 
                                   headers=headers)
        else:
            raise Exception(f"Unknown method {self.method}")
            
        response.raise_for_status()
        
        # Parse response
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        return Result.parse(BytesIO(response.content), content_type=content_type)
    
    def update(self, query: str, default_graph: Optional[str] = None,
               named_graph: Optional[str] = None) -> None:
        """
        Execute SPARQL update with AWS IAM authentication.
        
        Args:
            query: SPARQL update string
            default_graph: Default graph URI
            named_graph: Named graph URI
        """
        if not self.update_endpoint:
            raise Exception("Update endpoint not set!")
            
        session = self._get_session()
        params = {}
        
        if default_graph is not None:
            params["using-graph-uri"] = default_graph
            
        if named_graph is not None:
            params["using-named-graph-uri"] = named_graph
            
        headers = {
            "Accept": self.response_mime_types(),
            "Content-Type": "application/sparql-update; charset=UTF-8",
        }
        
        response = session.post(self.update_endpoint, params=params,
                               data=query.encode('utf-8'), headers=headers)
        response.raise_for_status()


class NeptuneSPARQLStore(SPARQLStore):
    """
    SPARQL Store for AWS Neptune with IAM authentication support.
    
    This store extends the standard SPARQLStore to add AWS SigV4 request signing
    for IAM-authenticated access to Neptune databases.
    """
    
    def __init__(self, *args, region_name=None, service_name='neptune-db', **kwargs):
        """
        Initialize Neptune SPARQL Store.
        
        Args:
            region_name: AWS region where Neptune instance is located
            service_name: AWS service name for signing (default: 'neptune-db')
            *args, **kwargs: Additional arguments passed to SPARQLStore
        """
        # Call parent init first
        super().__init__(*args, **kwargs)
        
        # Create custom connector with Neptune authentication after parent init
        self._connector = NeptuneSPARQLConnector(
            query_endpoint=self.query_endpoint,
            region_name=region_name,
            service_name=service_name,
            method=kwargs.get('method', 'POST'),
            returnFormat=kwargs.get('returnFormat', 'json')
        )
        
        # Replace the connector
        self.sparql = self._connector
        
    def _inject_prefixes(self, query, extra_bindings):
        """
        Inject prefix definitions into SPARQL query.
        
        Args:
            query: SPARQL query string
            extra_bindings: Dictionary of namespace bindings to inject
            
        Returns:
            Query string with prefixes injected
        """
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])


class NeptuneSPARQLUpdateStore(SPARQLUpdateStore):
    """
    SPARQL Update Store for AWS Neptune with IAM authentication support.
    
    This store extends the standard SPARQLUpdateStore to add AWS SigV4 request signing
    for IAM-authenticated access to Neptune databases. It supports both read and write
    operations with proper authentication.
    """
    
    def __init__(self, *args, region_name=None, service_name='neptune-db', **kwargs):
        """
        Initialize Neptune SPARQL Update Store.
        
        Args:
            region_name: AWS region where Neptune instance is located
            service_name: AWS service name for signing (default: 'neptune-db')
            *args, **kwargs: Additional arguments passed to SPARQLUpdateStore
        """
        # Store region info before parent init
        self.region_name = region_name
        self.service_name = service_name
        
        # Call parent init
        self.publish = None
        super().__init__(*args, **kwargs)
        
        # Create and set custom connector with Neptune authentication
        self._connector = NeptuneSPARQLConnector(
            query_endpoint=self.query_endpoint,
            update_endpoint=self.update_endpoint,
            region_name=region_name,
            service_name=service_name,
            method=kwargs.get('method', 'POST'),
            returnFormat=kwargs.get('returnFormat', 'json')
        )
        self.sparql = self._connector
    
    def _inject_prefixes(self, query, extra_bindings):
        """
        Inject prefix definitions into SPARQL query.
        
        Args:
            query: SPARQL query string
            extra_bindings: Dictionary of namespace bindings to inject
            
        Returns:
            Query string with prefixes injected
        """
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])
    
    def query(self, query, initNs=None, initBindings=None, queryGraph=None, DEBUG=False):
        """
        Execute a SPARQL query with AWS IAM authentication.
        
        This method overrides the parent query method to inject AWS authentication
        into the request.
        
        Args:
            query: SPARQL query string
            initNs: Initial namespace bindings
            initBindings: Initial variable bindings
            queryGraph: Target graph for the query
            DEBUG: Enable debug output
            
        Returns:
            Query results
        """
        if initBindings:
            v = list(initBindings)
            values = "\nVALUES ( %s )\n{ ( %s ) }\n" % (
                " ".join("?" + str(x) for x in v),
                " ".join(self.node_to_sparql(initBindings[x]) for x in v),
            )
            query = re.sub(r'where\s+{', 'WHERE {%s' % values, query, count=1, flags=re.I)
        return SPARQLUpdateStore.query(self, query, initNs=initNs, initBindings=None,
                                 queryGraph=queryGraph, DEBUG=DEBUG)

