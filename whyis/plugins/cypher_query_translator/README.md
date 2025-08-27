# Cypher Query Translator Plugin Configuration Example

## Enable the plugin in your Whyis configuration

Add the plugin to your PLUGINENGINE_PLUGINS list:

```python
PLUGINENGINE_PLUGINS = [
    'whyis_sparql_entity_resolver',
    'whyis_cypher_query_translator'
]
```

## Configuration Options

### CYPHER_DB
Database to query against (default: 'knowledge')
```python
CYPHER_DB = 'knowledge'
```

### CYPHER_JSONLD_CONTEXT
JSON-LD context for mapping non-prefixed Cypher terms to URIs:
```python
CYPHER_JSONLD_CONTEXT = {
    "Person": "http://schema.org/Person",
    "Organization": "http://schema.org/Organization", 
    "name": "http://schema.org/name",
    "email": "http://schema.org/email",
    "knows": "http://schema.org/knows",
    "worksFor": "http://schema.org/worksFor",
    "ex": "http://example.org/",
    "foaf": "http://xmlns.com/foaf/0.1/"
}
```

## Usage Examples

### Basic Node Query
```cypher
MATCH (p:Person) RETURN p
```

### Property Filtering
```cypher
MATCH (p:Person) 
WHERE p.name = 'Alice' 
RETURN p.name, p.email
```

### Relationship Query
```cypher
MATCH (a:Person)-[:KNOWS]->(b:Person) 
RETURN a.name, b.name
```

### Property Patterns with Reification
The plugin automatically handles RDF reification for property statements:
```cypher
MATCH (p:Person {name: 'John', age: '30'}) 
RETURN p
```

This gets translated to SPARQL with reification statements for complex property handling.

## HTTP API

### /cypher Endpoint
The plugin exposes a `/cypher` endpoint for HTTP requests:

```bash
curl -X POST http://localhost:5000/cypher \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (p:Person) WHERE p.name = \"Alice\" RETURN p.name",
    "context": {
      "Person": "http://schema.org/Person",
      "name": "http://schema.org/name"
    }
  }'
```

### /cql Blueprint
A full RESTful CQL blueprint is available at `/cql` that provides:
- Web interface at `/cql.html` 
- Translation-only mode with `translate-only` parameter
- Same functionality as `/sparql` but for CQL queries

```bash
# Execute CQL query
curl -X POST http://localhost:5000/cql \
  -d "query=MATCH (p:Person) RETURN p"

# Get SPARQL translation only
curl -X POST http://localhost:5000/cql \
  -d "query=MATCH (p:Person) RETURN p&translate-only=true"
```

## Integration

The plugin integrates with the Whyis listener system. You can programmatically execute Cypher queries:

```python
from flask import current_app

# Find the Cypher resolver
cypher_resolver = None
for listener in current_app.listeners:
    if isinstance(listener, CypherQueryResolver):
        cypher_resolver = listener
        break

if cypher_resolver:
    results = cypher_resolver.on_cypher_query(
        "MATCH (p:Person) RETURN p.name",
        context={"Person": "http://schema.org/Person", "name": "http://schema.org/name"}
    )
```