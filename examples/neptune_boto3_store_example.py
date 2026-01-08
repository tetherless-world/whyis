#!/usr/bin/env python3
"""
Example: Using NeptuneBoto3Store with AWS Neptune

This script demonstrates how to use the NeptuneBoto3Store class to connect
to Amazon Neptune with automatic credential management.
"""

from rdflib import ConjunctiveGraph, Namespace, Literal, URIRef
from whyis.plugins.neptune import NeptuneBoto3Store

# Example 1: Basic usage with automatic instance metadata retrieval
def example_basic():
    """
    Basic example: Connect to Neptune with automatic credential discovery.
    
    When running on EC2 with an IAM role, credentials are automatically
    retrieved from instance metadata.
    """
    print("Example 1: Basic usage with automatic credential discovery")
    
    store = NeptuneBoto3Store(
        query_endpoint='https://my-neptune.us-east-1.neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://my-neptune.us-east-1.neptune.amazonaws.com:8182/sparql',
        region_name='us-east-1'
    )
    
    graph = ConjunctiveGraph(store)
    
    # Example query
    results = graph.query("""
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o .
        }
        LIMIT 10
    """)
    
    for row in results:
        print(f"Subject: {row.s}, Predicate: {row.p}, Object: {row.o}")


# Example 2: Using custom boto3 session
def example_custom_session():
    """
    Advanced example: Use a custom boto3 session with explicit credentials.
    """
    import boto3
    
    print("Example 2: Custom boto3 session")
    
    # Create custom session (could use profile, explicit credentials, etc.)
    session = boto3.Session(
        aws_access_key_id='YOUR_ACCESS_KEY',
        aws_secret_access_key='YOUR_SECRET_KEY',
        region_name='us-east-1'
    )
    
    store = NeptuneBoto3Store(
        query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://neptune.amazonaws.com:8182/sparql',
        region_name='us-east-1',
        boto3_session=session
    )
    
    graph = ConjunctiveGraph(store)
    print(f"Graph store: {type(graph.store).__name__}")


# Example 3: Disable instance metadata
def example_no_instance_metadata():
    """
    Example: Disable instance metadata and use only boto3 session credentials.
    
    Useful when you want to avoid the instance metadata service or when
    running outside of EC2.
    """
    print("Example 3: Disable instance metadata")
    
    store = NeptuneBoto3Store(
        query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://neptune.amazonaws.com:8182/sparql',
        region_name='us-west-2',
        use_instance_metadata=False  # Only use boto3 session credentials
    )
    
    graph = ConjunctiveGraph(store)
    print(f"Instance metadata disabled: {not store.use_instance_metadata}")


# Example 4: SPARQL query with authentication
def example_sparql_query():
    """
    Example: Execute a SPARQL query with automatic AWS authentication.
    """
    print("Example 4: SPARQL query")
    
    store = NeptuneBoto3Store(
        query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://neptune.amazonaws.com:8182/sparql',
        region_name='us-east-1'
    )
    
    graph = ConjunctiveGraph(store)
    
    # Define namespaces
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    
    # Query for people
    query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?person ?name
        WHERE {
            ?person a foaf:Person .
            ?person foaf:name ?name .
        }
        LIMIT 10
    """
    
    results = graph.query(query)
    
    for row in results:
        print(f"Person: {row.person}, Name: {row.name}")


# Example 5: Custom service name (for Neptune alternatives)
def example_custom_service():
    """
    Example: Use custom service name for request signing.
    """
    print("Example 5: Custom service name")
    
    store = NeptuneBoto3Store(
        query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://neptune.amazonaws.com:8182/sparql',
        region_name='eu-west-1',
        service_name='custom-service'  # Custom AWS service name
    )
    
    print(f"Service name: {store.service_name}")


if __name__ == '__main__':
    print("NeptuneBoto3Store Examples")
    print("=" * 60)
    
    # Note: These examples require actual Neptune endpoints and credentials
    # Uncomment the example you want to run:
    
    # example_basic()
    # example_custom_session()
    # example_no_instance_metadata()
    # example_sparql_query()
    # example_custom_service()
    
    print("\nNote: Update the endpoint URLs and ensure AWS credentials are configured")
    print("before running these examples.")
