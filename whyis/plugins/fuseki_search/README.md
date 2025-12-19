# Fuseki Search Plugin

This plugin provides full-text search capabilities using Apache Jena Fuseki's text search functionality.

## Overview

The Fuseki Search plugin integrates with Apache Jena Fuseki's full-text search using the `text:search` predicate. It provides:
- Entity resolution via full-text search
- Search data view for the search interface
- Support for context-aware and type-filtered search

## Configuration

To use this plugin, set the following configuration in your Whyis application:

```python
RESOLVER_TYPE = 'fuseki'  # or 'sparql' (both use this plugin)
RESOLVER_DB = 'knowledge'  # name of the database to search
PLUGINENGINE_PLUGINS = ['whyis_fuseki_search']
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

The plugin uses Apache Jena's text search syntax:

```sparql
(?label ?relevance) text:search 'search_term'.
```

This requires that Fuseki is configured with a text index. See [Jena Text Search documentation](https://jena.apache.org/documentation/query/text-query.html) for configuration details.

## Fuseki Text Index Configuration

To use this plugin effectively, your Fuseki server must be configured with a text index. Example configuration:

```turtle
<#text_dataset> rdf:type text:TextDataset ;
    text:dataset <#dataset> ;
    text:index <#indexLucene> .

<#indexLucene> a text:TextIndexLucene ;
    text:directory <file:Lucene> ;
    text:entityMap <#entMap> .

<#entMap> a text:EntityMap ;
    text:entityField      "uri" ;
    text:defaultField     "label" ;
    text:map (
         [ text:field "label" ; text:predicate rdfs:label ]
         [ text:field "prefLabel" ; text:predicate skos:prefLabel ]
         [ text:field "title" ; text:predicate dc:title ]
    ) .
```

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
