#!/usr/bin/env python3
"""
Demo script for the CQL blueprint functionality.

This script demonstrates how to use the CQL (Cypher Query Language) blueprint
to translate CQL queries to SPARQL and execute them.
"""

import requests
import json
import sys

def demo_cql_endpoint(base_url="http://localhost:5000"):
    """Demonstrate the CQL endpoint functionality."""
    
    print("=== CQL Blueprint Demo ===\n")
    
    # Example CQL queries
    queries = [
        {
            "name": "Find all persons",
            "query": "MATCH (p:Person) RETURN p"
        },
        {
            "name": "Find person by name",
            "query": "MATCH (p:Person) WHERE p.name = 'Alice' RETURN p.name, p.email"
        },
        {
            "name": "Find relationships",
            "query": "MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN a.name, b.name"
        }
    ]
    
    # JSON-LD context for URI mappings
    context = {
        "Person": "http://schema.org/Person",
        "name": "http://schema.org/name",
        "email": "http://schema.org/email",
        "knows": "http://schema.org/knows"
    }
    
    cql_url = f"{base_url}/cql"
    
    for query_info in queries:
        print(f"Query: {query_info['name']}")
        print(f"CQL: {query_info['query']}")
        print("-" * 50)
        
        # First, get the SPARQL translation
        print("1. Getting SPARQL translation (translate-only=true):")
        try:
            response = requests.post(cql_url, 
                                   data={
                                       "query": query_info['query'],
                                       "translate-only": "true"
                                   },
                                   timeout=10)
            
            if response.status_code == 200:
                print("SPARQL Translation:")
                print(response.text)
            else:
                print(f"Error getting translation: {response.status_code}")
                print(response.text)
                
        except requests.RequestException as e:
            print(f"Connection error: {e}")
        
        print("\n2. Executing CQL query:")
        try:
            response = requests.post(cql_url,
                                   json={
                                       "query": query_info['query'],
                                       "context": context
                                   },
                                   timeout=10)
            
            if response.status_code == 200:
                print("Query Results:")
                print(response.text[:500])  # Truncate for demo
                if len(response.text) > 500:
                    print("... (truncated)")
            else:
                print(f"Error executing query: {response.status_code}")
                print(response.text)
                
        except requests.RequestException as e:
            print(f"Connection error: {e}")
        
        print("=" * 60)
        print()

def demo_direct_translation():
    """Demonstrate direct translation without HTTP."""
    
    print("=== Direct Translation Demo ===\n")
    
    try:
        from whyis.plugins.cypher_query_translator.plugin import CypherToSparqlTranslator
        
        # Create translator with context
        context = {
            "Person": "http://schema.org/Person",
            "name": "http://schema.org/name",
            "knows": "http://schema.org/knows"
        }
        
        translator = CypherToSparqlTranslator(context)
        
        # Example queries
        queries = [
            "MATCH (p:Person) RETURN p",
            "MATCH (p:Person) WHERE p.name = 'Alice' RETURN p.name",
            "MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN a.name, b.name"
        ]
        
        for query in queries:
            print(f"CQL: {query}")
            print("SPARQL:")
            sparql = translator.translate(query)
            print(sparql)
            print("-" * 50)
            
    except ImportError as e:
        print(f"Cannot import translator: {e}")
        print("This demo requires the Whyis environment to be set up.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "direct":
        demo_direct_translation()
    else:
        demo_cql_endpoint()
        print("\nTip: Run with 'direct' argument to see translation without HTTP:")
        print("python cql_blueprint_demo.py direct")