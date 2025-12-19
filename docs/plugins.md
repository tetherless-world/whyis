# Search Plugins

Whyis supports multiple full-text search backends through a plugin system. Search plugins provide entity resolution and full-text search capabilities across your knowledge graph.

## Available Plugins

### Fuseki Search Plugin

The **Fuseki Search Plugin** (`whyis_fuseki_search`) integrates with Apache Jena Fuseki's text search functionality using Apache Lucene.

**Use this plugin when:**
- Using Apache Jena Fuseki as your triple store
- You have Fuseki configured with a text index
- Running Whyis in standard on-premise or self-hosted environments

**Configuration:**
```python
RESOLVER_TYPE = 'fuseki'  # or 'sparql'
RESOLVER_DB = 'knowledge'
PLUGINENGINE_PLUGINS = ['whyis_fuseki_search']
```

See [fuseki_search plugin documentation](../whyis/plugins/fuseki_search/README.md) for detailed setup instructions.

### Neptune Search Plugin

The **Neptune Search Plugin** (`whyis_neptune_search`) integrates with AWS Neptune's OpenSearch full-text search.

**Use this plugin when:**
- Using AWS Neptune as your triple store
- You have Neptune configured with OpenSearch integration
- Running Whyis in AWS cloud environments

**Configuration:**
```python
RESOLVER_TYPE = 'neptune'
RESOLVER_DB = 'knowledge'
PLUGINENGINE_PLUGINS = ['whyis_neptune_search']
```

See [neptune_search plugin documentation](../whyis/plugins/neptune_search/README.md) for detailed setup instructions.

## Choosing a Search Plugin

The choice of search plugin depends on your triple store backend:

| Triple Store | Plugin | Search Backend |
|-------------|---------|----------------|
| Apache Jena Fuseki | `whyis_fuseki_search` | Apache Lucene |
| AWS Neptune | `whyis_neptune_search` | Amazon OpenSearch |
| Other SPARQL endpoints with text: namespace | `whyis_fuseki_search` | Varies |

## Configuration Options

Both plugins support the following configuration options:

### RESOLVER_TYPE
The type of resolver to use. Valid values:
- `'fuseki'` or `'sparql'` - Uses Fuseki Search Plugin
- `'neptune'` - Uses Neptune Search Plugin

Default: `'fuseki'`

### RESOLVER_DB
The name of the database to search.

Default: `'knowledge'`

### PLUGINENGINE_PLUGINS
List of plugins to load. Include the appropriate search plugin:

```python
PLUGINENGINE_PLUGINS = ['whyis_fuseki_search']  # For Fuseki
# or
PLUGINENGINE_PLUGINS = ['whyis_neptune_search']  # For Neptune
```

## Entity Resolution

Both plugins implement entity resolution, which allows you to search for entities by term. The resolve view is accessible at:

```
/?view=resolve&term=<search_term>
```

Optional parameters:
- `type` - Filter results by RDF type
- `context` - Context term for relevance boosting

Example:
```
/?view=resolve&term=protein&type=http://example.org/Protein
```

## Search Data View

Both plugins provide a search data view that returns JSON results. This is used by the search interface and is accessible at:

```
/home?view=search_data&query=<search_term>
```

Example:
```
/home?view=search_data&query=enzyme
```

## Implementation Details

### Query Differences

The main difference between the plugins is the SPARQL syntax used:

**Fuseki Search:**
```sparql
(?label ?relevance) text:search 'search_term'.
```

**Neptune Search:**
```sparql
SERVICE <http://aws.amazon.com/neptune/vocab/v01/services/fts> {
  [] fts:search 'search_term' ;
     fts:matchQuery '*' ;
     fts:entity ?node ;
     fts:score ?relevance .
}
```

Neptune uses a SERVICE clause to invoke OpenSearch integration, while Fuseki uses a direct predicate-based approach with Apache Lucene.

### Searched Properties

Both plugins search across these RDF properties:
- `dc:title`
- `rdfs:label`
- `skos:prefLabel`
- `skos:altLabel`
- `foaf:name`
- `dc:identifier`
- `schema:name`
- `skos:notation`

### Filtered Resource Types

Both plugins exclude these resource types from results:
- Semantic Science Integrated Ontology terms
- Nanopublication metadata (Nanopublication, Assertion, Provenance, PublicationInfo)

## Extending Search

To create a custom search plugin:

1. Create a new plugin directory under `whyis/plugins/`
2. Implement an `EntityResolverListener` subclass with `on_resolve` method
3. Create a `Plugin` subclass that registers the resolver
4. Add templates for search views
5. Register the plugin in `setup.py` entry_points

See the existing plugins as examples:
- [fuseki_search/plugin.py](../whyis/plugins/fuseki_search/plugin.py)
- [neptune_search/plugin.py](../whyis/plugins/neptune_search/plugin.py)

## Troubleshooting

### No search results

1. Verify the search index is configured correctly for your triple store
2. Check that the `RESOLVER_TYPE` matches your triple store
3. Ensure the appropriate plugin is listed in `PLUGINENGINE_PLUGINS`
4. Verify that data has been indexed (may require rebuild/reindex)

### Wrong plugin loaded

Check your configuration:
```python
# Verify RESOLVER_TYPE
print(app.config['RESOLVER_TYPE'])

# Verify loaded plugins
print(app.config['PLUGINENGINE_PLUGINS'])
```

### Import errors

Ensure the plugin is properly installed:
```bash
pip install -e .
```

This will register the plugin entry points from `setup.py`.
