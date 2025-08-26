#!/usr/bin/env python3
"""
Example script demonstrating the Cypher to SPARQL translator functionality.
"""

from whyis.plugins.cypher_query_translator.plugin import CypherToSparqlTranslator

def main():
    """Demonstrate Cypher to SPARQL translation with examples."""
    
    # JSON-LD context for mapping terms to URIs
    context = {
        "Person": "http://schema.org/Person",
        "Organization": "http://schema.org/Organization",
        "name": "http://schema.org/name",
        "email": "http://schema.org/email", 
        "knows": "http://schema.org/knows",
        "worksFor": "http://schema.org/worksFor",
        "age": "http://schema.org/age"
    }
    
    translator = CypherToSparqlTranslator(context)
    
    # Example 1: Simple node query
    print("=== Example 1: Simple Node Query ===")
    cypher1 = "MATCH (p:Person) RETURN p"
    sparql1 = translator.translate(cypher1)
    print(f"Cypher: {cypher1}")
    print(f"SPARQL:\n{sparql1}\n")
    
    # Example 2: Property filtering
    print("=== Example 2: Property Filtering ===")
    cypher2 = "MATCH (p:Person) WHERE p.name = 'Alice' RETURN p.name, p.email"
    sparql2 = translator.translate(cypher2)
    print(f"Cypher: {cypher2}")
    print(f"SPARQL:\n{sparql2}\n")
    
    # Example 3: Multiple properties
    print("=== Example 3: Multiple Properties ===") 
    cypher3 = "MATCH (p:Person) WHERE p.age = '30' RETURN p.name, p.age"
    sparql3 = translator.translate(cypher3)
    print(f"Cypher: {cypher3}")
    print(f"SPARQL:\n{sparql3}\n")
    
    # Example 4: Property patterns with reification
    print("=== Example 4: Property Patterns (demonstrates reification) ===")
    patterns = translator._parse_property_patterns("{name: 'John', age: '30'}")
    print("Property patterns with RDF reification:")
    for pattern in patterns:
        print(f"  {pattern}")
    print()
    
    # Example 5: Context expansion
    print("=== Example 5: Context Expansion ===")
    print(f"'Person' expands to: {translator.expand_uri('Person')}")
    print(f"'name' expands to: {translator.expand_uri('name')}")
    print(f"'unknown' expands to: {translator.expand_uri('unknown')}")
    print()

if __name__ == '__main__':
    main()