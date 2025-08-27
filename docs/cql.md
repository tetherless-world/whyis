# CQL (Cypher Query Language) Blueprint

The CQL blueprint provides a RESTful endpoint for executing Cypher queries against Whyis RDF data by automatically translating them to SPARQL.

## Overview

The CQL blueprint is located at `/cql` and provides functionality similar to the `/sparql` endpoint but accepts CQL/Cypher queries instead. It leverages the existing Cypher Query Translator plugin to convert CQL queries to SPARQL and execute them against the RDF graph.

## Features

- **CQL to SPARQL Translation**: Automatically converts Cypher queries to equivalent SPARQL queries
- **JSON-LD Context Support**: Uses configurable URI mappings for non-prefixed terms
- **Translation-Only Mode**: Returns the generated SPARQL query without execution when `translate-only` parameter is provided
- **Web Interface**: Provides a user-friendly form interface similar to the SPARQL endpoint
- **RESTful API**: Supports both GET and POST requests with proper content negotiation

## Usage

### Web Interface

Navigate to `/cql.html` in your browser to access the interactive CQL query interface. The interface includes:

- A text editor for writing CQL queries
- A checkbox option to show SPARQL translation only
- Example CQL queries to get started
- Results display in table format

### HTTP API

#### Execute CQL Query

```bash
curl -X POST http://localhost:5000/cql \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=MATCH (p:Person) WHERE p.name = 'Alice' RETURN p.name"
```

#### Get SPARQL Translation Only

```bash
curl -X POST http://localhost:5000/cql \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=MATCH (p:Person) RETURN p&translate-only=true"
```

#### With JSON-LD Context

```bash
curl -X POST http://localhost:5000/cql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (p:Person) WHERE p.name = \"Alice\" RETURN p.name",
    "context": {
      "Person": "http://schema.org/Person",
      "name": "http://schema.org/name"
    }
  }'
```

## Supported CQL Syntax

The CQL blueprint supports a subset of Cypher query language including:

### Node Patterns
```cypher
MATCH (p:Person)          # Match nodes with type Person
MATCH (p)                 # Match any node
```

### Property Filters
```cypher
WHERE p.name = 'Alice'    # Property equality
WHERE p.age > 25          # Comparison operators
```

### Return Clauses
```cypher
RETURN p                  # Return entire node
RETURN p.name, p.email    # Return specific properties
```

### Relationship Patterns
```cypher
MATCH (a:Person)-[:KNOWS]->(b:Person)  # Directed relationships
```

## Configuration

The CQL blueprint uses the same configuration as the Cypher Query Translator plugin:

```python
# In your Whyis configuration
CYPHER_DB = 'knowledge'  # Database to query against
CYPHER_JSONLD_CONTEXT = {
    "Person": "http://schema.org/Person",
    "name": "http://schema.org/name",
    "knows": "http://schema.org/knows"
}
```

## Implementation Details

The CQL blueprint consists of:

- `cql_blueprint.py`: Blueprint definition
- `cql_view.py`: Request handling and query processing
- `cql_form.py`: Web interface form handler
- `cql.html`: Template for the web interface

### Request Flow

1. CQL query received via GET or POST request
2. Check for `translate-only` parameter
3. Initialize CypherToSparqlTranslator with JSON-LD context
4. Translate CQL query to SPARQL
5. If `translate-only` is true, return SPARQL as plain text
6. Otherwise, execute SPARQL query against the RDF graph
7. Return results in the requested format

## Error Handling

The blueprint handles various error conditions:

- Missing query parameter returns 400 Bad Request
- Translation errors return 500 Internal Server Error with details
- Authentication follows the same patterns as other Whyis endpoints

## Security

The CQL blueprint includes the same security features as other Whyis blueprints:

- `@conditional_login_required` decorator for authentication
- No support for UPDATE operations (read-only queries)
- Request validation and sanitization

## See Also

- [Cypher Query Translator Plugin](../plugins/cypher_query_translator/)
- [SPARQL Blueprint](sparql.md)
- [Whyis Architecture Overview](../architecture.md)