# -*- coding:utf-8 -*-

from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
#from rdflib.plugins.stores.sparqlconnector import SPARQLConnectorException, _response_mime_types
import re

class WhyisSPARQLUpdateStore(SPARQLUpdateStore):
    # To resolve linter warning
    # "attribute defined outside  __init__"
    def __init__(self, *args, **kwargs):
        self.publish = None
        SPARQLUpdateStore.__init__(self, *args, **kwargs)

    def _inject_prefixes(self, query, extra_bindings):
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])

    def query(self, query, initNs=None, initBindings=None, queryGraph=None, DEBUG=False):
        if initBindings:
            v = list(initBindings)
            values = "\nVALUES ( %s )\n{ ( %s ) }\n" % (
                " ".join("?" + str(x) for x in v),
                " ".join(self.node_to_sparql(initBindings[x]) for x in v),
            )
            query = re.sub(r'where\s+{', 'WHERE {%s' % values, query, count=1, flags=re.I)
        return SPARQLUpdateStore.query(self, query, initNs=initNs, initBindings=None,
                                 queryGraph=queryGraph, DEBUG=DEBUG)
    
    def raw_sparql_request(self, method, params=None, data=None, headers=None):
        """
        Make a raw SPARQL endpoint request with authentication.
        
        This method is used by the SPARQL blueprint to proxy requests.
        For stores with HTTP Basic Auth, it uses the store's auth attribute.
        
        Args:
            method (str): HTTP method ('GET' or 'POST')
            params (dict): Query parameters
            data: Request body data
            headers (dict): Request headers
            
        Returns:
            Response object from requests library
        """
        import requests
        from urllib.parse import urlencode
        
        # Use query_endpoint for all SPARQL requests
        url = self.query_endpoint
        
        # Build URL with parameters if any
        if params:
            qsa = "?" + urlencode(params)
            url = url + qsa
        
        # Prepare headers
        request_headers = dict(headers) if headers else {}
        
        # Make request with authentication if available
        kwargs = {}
        if hasattr(self, 'auth') and self.auth is not None:
            kwargs['auth'] = self.auth
        
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=request_headers,
            data=data,
            **kwargs
        )
        
        return response
