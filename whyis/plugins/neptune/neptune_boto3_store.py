# -*- coding:utf-8 -*-
"""
Neptune Boto3 SPARQL Store

This module provides a subclass of RDFlib's SPARQLUpdateStore that uses boto3
for AWS credential management and request signing. This provides more robust
credential handling compared to manual AWS authentication.

The NeptuneBoto3Store class automatically signs all HTTP requests to Neptune
using AWS SigV4 signatures, leveraging boto3's built-in credential discovery
mechanisms including InstanceMetadataProvider for EC2 instances.
"""

import logging
from urllib.parse import urlparse, parse_qs
from io import BytesIO

try:
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import InstanceMetadataProvider, InstanceMetadataFetcher
except ImportError:
    boto3 = None
    SigV4Auth = None
    AWSRequest = None
    InstanceMetadataProvider = None
    InstanceMetadataFetcher = None

from whyis.database.whyis_sparql_update_store import WhyisSPARQLUpdateStore

logger = logging.getLogger(__name__)


class NeptuneBoto3Store(WhyisSPARQLUpdateStore):
    """
    A SPARQL store that uses boto3 credentials for AWS Neptune authentication.
    
    This store extends WhyisSPARQLUpdateStore and automatically signs all HTTP
    requests using AWS SigV4 signatures via boto3's request signing capabilities.
    
    Credentials are dynamically retrieved using boto3's credential chain, with
    special support for EC2 instance metadata via InstanceMetadataProvider and
    InstanceMetadataFetcher for IAM role credentials.
    
    Attributes:
        region_name (str): AWS region where Neptune is located
        service_name (str): AWS service name for signing (default: 'neptune-db')
        boto3_session: Boto3 session for credential management
        use_instance_metadata (bool): Whether to prioritize instance metadata credentials
        
    Example:
        >>> from rdflib import ConjunctiveGraph
        >>> store = NeptuneBoto3Store(
        ...     query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        ...     update_endpoint='https://neptune.amazonaws.com:8182/sparql',
        ...     region_name='us-east-1'
        ... )
        >>> graph = ConjunctiveGraph(store)
    """
    
    def __init__(self, query_endpoint=None, update_endpoint=None, 
                 region_name=None, service_name='neptune-db',
                 boto3_session=None, use_instance_metadata=True, **kwargs):
        """
        Initialize the Neptune Boto3 Store.
        
        Args:
            query_endpoint (str): SPARQL query endpoint URL
            update_endpoint (str): SPARQL update endpoint URL
            region_name (str): AWS region name (required)
            service_name (str): AWS service name for signing (default: 'neptune-db')
            boto3_session: Optional boto3 Session object. If not provided, 
                          a new session will be created using default credentials.
            use_instance_metadata (bool): If True (default), dynamically fetch credentials
                                         from EC2 instance metadata when available.
            **kwargs: Additional arguments passed to WhyisSPARQLUpdateStore
            
        Raises:
            ValueError: If region_name is not provided
            ImportError: If boto3 is not installed
        """
        # Import boto3 here so it's only required when this store is used
        if boto3 is None:
            raise ImportError(
                "boto3 is required for NeptuneBoto3Store. "
                "Install it with: pip install boto3"
            )
        
        if not region_name:
            raise ValueError("region_name is required for NeptuneBoto3Store")
        
        # Store AWS configuration
        self.region_name = region_name
        self.service_name = service_name
        self.use_instance_metadata = use_instance_metadata
        
        # Create or use provided boto3 session
        if boto3_session is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3_session
        
        # Set up instance metadata provider if requested
        self._instance_metadata_provider = None
        if self.use_instance_metadata:
            try:
                # Create instance metadata fetcher and provider
                fetcher = InstanceMetadataFetcher()
                self._instance_metadata_provider = InstanceMetadataProvider(
                    iam_role_fetcher=fetcher
                )
                logger.info("Instance metadata provider initialized for dynamic credential retrieval")
            except Exception as e:
                logger.warning(f"Could not initialize instance metadata provider: {e}")
                self._instance_metadata_provider = None
        
        # Get initial credentials from boto3 session
        self.credentials = self.boto3_session.get_credentials()
        if self.credentials is None and self._instance_metadata_provider is None:
            raise ValueError(
                "No AWS credentials found. Configure credentials using "
                "environment variables, ~/.aws/credentials, or IAM roles."
            )
        
        # Initialize parent class without custom_requests
        # We'll override the methods that make HTTP requests
        super().__init__(
            query_endpoint=query_endpoint,
            update_endpoint=update_endpoint,
            **kwargs
        )
        
        logger.info(
            f"Initialized NeptuneBoto3Store with region={region_name}, "
            f"service={service_name}, use_instance_metadata={use_instance_metadata}"
        )
    
    def _get_credentials(self):
        """
        Get current AWS credentials, dynamically fetching from instance metadata if configured.
        
        This method attempts to get credentials in the following order:
        1. If use_instance_metadata is True, try InstanceMetadataProvider first
        2. Fall back to boto3 session credentials
        
        Returns:
            Frozen credentials object with access_key, secret_key, and token
        """
        credentials = None
        
        # Try instance metadata provider first if configured
        if self.use_instance_metadata and self._instance_metadata_provider:
            try:
                credentials = self._instance_metadata_provider.load()
                if credentials:
                    logger.debug("Using credentials from instance metadata provider")
                    return credentials.get_frozen_credentials()
            except Exception as e:
                logger.debug(f"Could not load credentials from instance metadata: {e}")
        
        # Fall back to boto3 session credentials
        credentials = self.boto3_session.get_credentials()
        if credentials:
            logger.debug("Using credentials from boto3 session")
            return credentials.get_frozen_credentials()
        
        raise ValueError(
            "Unable to locate credentials. Configure credentials using "
            "environment variables, ~/.aws/credentials, IAM roles, or instance metadata."
        )
    
    def _sign_request(self, method, url, headers=None, body=None):
        """
        Sign an HTTP request using AWS SigV4 with boto3 credentials.
        
        Dynamically retrieves credentials (potentially from instance metadata)
        for each request to ensure credentials are always current.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): Full URL including query parameters
            headers (dict): HTTP headers
            body: Request body (str or bytes)
            
        Returns:
            dict: Updated headers with AWS signature
        """
        # Get current credentials (handles credential refresh and instance metadata)
        frozen_credentials = self._get_credentials()
        
        # Parse URL to separate path and query string
        parsed = urlparse(url)
        
        # Create AWS request object
        request = AWSRequest(
            method=method,
            url=url,
            headers=headers or {},
            data=body
        )
        
        # Sign the request
        signer = SigV4Auth(frozen_credentials, self.service_name, self.region_name)
        signer.add_auth(request)
        
        return dict(request.headers)
    
    def _request(self, method, url, headers=None, body=None):
        """
        Make an authenticated HTTP request to Neptune.
        
        This method signs the request using AWS SigV4 and sends it.
        
        Args:
            method (str): HTTP method
            url (str): Request URL
            headers (dict): Request headers
            body: Request body
            
        Returns:
            Response object from requests library
        """
        import requests
        
        # Sign the request
        signed_headers = self._sign_request(method, url, headers, body)
        
        # Make the request
        session = requests.Session()
        response = session.request(
            method=method,
            url=url,
            headers=signed_headers,
            data=body
        )
        
        return response
    
    def query(self, query, default_graph=None, named_graph=None):
        """
        Execute a SPARQL query with AWS SigV4 authentication.
        
        Overrides SPARQLConnector.query() to use authenticated HTTP requests.
        
        Args:
            query (str): SPARQL query string
            default_graph: Default graph URI
            named_graph: Named graph URI
            
        Returns:
            Query results from rdflib Result.parse()
        """
        from urllib.parse import urlencode
        from io import BytesIO
        from rdflib.query import Result
        
        if not self.query_endpoint:
            raise ValueError("Query endpoint not set!")
        
        # Build query parameters
        params = {}
        if default_graph is not None:
            from rdflib.term import BNode
            if not isinstance(default_graph, BNode):
                params["default-graph-uri"] = default_graph
        
        # Build headers
        headers = {"Accept": self.response_mime_types()}
        
        # Make authenticated request based on method
        if self.method == "POST":
            headers["Content-Type"] = "application/sparql-query"
            qsa = "?" + urlencode(params) if params else ""
            url = self.query_endpoint + qsa
            
            response = self._request(
                method="POST",
                url=url,
                headers=headers,
                body=query.encode('utf-8')
            )
        else:  # GET or POST_FORM
            params["query"] = query
            qsa = "?" + urlencode(params)
            url = self.query_endpoint + qsa
            
            if self.method == "GET":
                response = self._request(
                    method="GET",
                    url=url,
                    headers=headers
                )
            else:  # POST_FORM
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = self._request(
                    method="POST",
                    url=self.query_endpoint,
                    headers=headers,
                    body=urlencode(params).encode('utf-8')
                )
        
        # Handle HTTP errors
        if not response.ok:
            raise IOError(f"HTTP Error {response.status_code}: {response.text}")
        
        # Parse the response
        content_type = response.headers.get('Content-Type', 'application/sparql-results+xml')
        if ';' in content_type:
            content_type = content_type.split(';')[0]
        
        return Result.parse(BytesIO(response.content), content_type=content_type)
    
    def update(self, query, default_graph=None, named_graph=None):
        """
        Execute a SPARQL update with AWS SigV4 authentication.
        
        Overrides SPARQLConnector.update() to use authenticated HTTP requests.
        
        Args:
            query (str): SPARQL update string
            default_graph: Default graph URI
            named_graph: Named graph URI
        """
        from urllib.parse import urlencode
        
        if not self.update_endpoint:
            raise ValueError("Update endpoint not set!")
        
        # Build parameters
        params = {}
        if default_graph is not None:
            params["using-graph-uri"] = default_graph
        if named_graph is not None:
            params["using-named-graph-uri"] = named_graph
        
        # Build headers
        headers = {
            "Accept": self.response_mime_types(),
            "Content-Type": "application/sparql-update; charset=UTF-8"
        }
        
        # Build URL with parameters
        qsa = "?" + urlencode(params) if params else ""
        url = self.update_endpoint + qsa
        
        # Make authenticated request
        response = self._request(
            method="POST",
            url=url,
            headers=headers,
            body=query.encode('utf-8')
        )
        
        # Handle HTTP errors
        if not response.ok:
            raise IOError(f"HTTP Error {response.status_code}: {response.text}")
