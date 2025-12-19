# Neptune Search Plugin

This plugin provides full-text search capabilities using AWS Neptune's OpenSearch integration.

## Overview

The Neptune Search plugin integrates with AWS Neptune's OpenSearch full-text search using the `fts:search` predicate. It provides:
- Entity resolution via full-text search
- Search data view for the search interface
- Support for context-aware and type-filtered search
- Compatible with Neptune's OpenSearch backend

## Configuration

To use this plugin, set the following configuration in your Whyis application:

```python
RESOLVER_TYPE = 'neptune'
RESOLVER_DB = 'knowledge'  # name of the database to search
PLUGINENGINE_PLUGINS = ['whyis_neptune_search']
```

## Features

### Entity Resolution

The plugin implements the `on_resolve` method to search entities by term, with optional filters:
- `term`: Search term (required)
- `type`: RDF type to filter results (optional)
- `context`: Context for relevance boosting (optional)
- `label`: Whether to fetch labels for results (default: True)

### Search View

The plugin registers a `search.json` view that provides full-text search results. This view is accessible via the `?view=search_data` parameter on the HomePage resource.

## SPARQL Query Syntax

The plugin uses AWS Neptune's full-text search syntax with OpenSearch:

```sparql
?label fts:search 'search_term' .
?label fts:score ?relevance .
```

This requires that Neptune is configured with OpenSearch integration enabled. See [Neptune Full-Text Search documentation](https://docs.aws.amazon.com/neptune/latest/userguide/full-text-search.html) for configuration details.

## Neptune OpenSearch Configuration

To use this plugin, your Neptune cluster must have:

1. **OpenSearch Integration Enabled**: Neptune must be configured to integrate with Amazon OpenSearch Service
2. **Full-Text Search Endpoint**: The Neptune cluster must have a full-text search endpoint configured
3. **Indexed Properties**: Properties to be searched must be indexed in OpenSearch

### Example Configuration Steps

1. Enable OpenSearch integration on your Neptune cluster
2. Configure the OpenSearch domain
3. Index the properties you want to search (see Search Properties below)
4. Ensure proper IAM roles and permissions are configured

For detailed setup instructions, refer to the [AWS Neptune documentation](https://docs.aws.amazon.com/neptune/latest/userguide/full-text-search.html).

## Search Properties

The plugin searches across multiple properties:
- `dc:title`
- `rdfs:label`
- `skos:prefLabel`
- `skos:altLabel`
- `foaf:name`
- `dc:identifier`
- `schema:name`
- `skos:notation`

## Filtered Resources

The following resource types are excluded from search results:
- `sio:Term` (Semantic Science Integrated Ontology terms)
- `np:Nanopublication`
- `np:Assertion`
- `np:Provenance`
- `np:PublicationInfo`

## Differences from Fuseki Search

The main differences between Neptune and Fuseki search plugins are:

1. **Namespace**: Neptune uses `fts:` (http://aws.amazon.com/neptune/vocab/v01/services/fts#) instead of `text:` (http://jena.apache.org/fulltext#)
2. **Query Syntax**: 
   - Fuseki: `(?label ?relevance) text:search 'term'`
   - Neptune: `?label fts:search 'term' . ?label fts:score ?relevance`
3. **Backend**: Fuseki uses Apache Lucene; Neptune uses Amazon OpenSearch Service
4. **Configuration**: Fuseki configuration is in assembler files; Neptune is configured via AWS console/API

## Connection String

When connecting to Neptune with OpenSearch, ensure your SPARQL endpoint URL includes the proper Neptune endpoint. Example:

```python
KNOWLEDGE_ENDPOINT = 'https://your-neptune-cluster.region.neptune.amazonaws.com:8182/sparql'
```

## IAM Authentication

Neptune typically requires IAM authentication. Ensure your application has proper AWS credentials configured with permissions to:
- Execute queries on Neptune
- Access the OpenSearch domain (if applicable)

Refer to the [Neptune IAM documentation](https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth.html) for authentication setup.
