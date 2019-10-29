# Configuring Whyis

Whyis is configured within a generated app using the file `config.py`. This includes a number of options that can be added or modified.
The file contains a baseline config object with customizations for production, development, and testing.

## Enabling Anonymous Access

By defualt, Whyis requires users to be authenticated to access the knowledge graph. 
Read-only anonymous access can be enabled by adding the following entry:

```
   DEFAULT_ANONYMOUS_READ=True,
```

## Using BlazeGraph Bulk Loading

Whyis can use the Blazegraph custom bulk loader API if configured. 
To use it with the default configuration, add the following entries to the config object:

```
    knowledge_useBlazeGraphBulkLoad = True,
    knowledge_bulkLoadEndpoint = 'http://localhost:8080/blazegraph/dataloader',
    knowledge_BlazeGraphProperties = '/apps/whyis/knowledge.properties',
    load_dir = '/data/loaded',
    knowledge_bulkLoadNamespace = 'knowledge',
    
```

