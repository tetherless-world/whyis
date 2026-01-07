# Neptune Plugin - AWS IAM Authentication Support

## Overview

This plugin provides AWS IAM authentication support for Amazon Neptune databases. It includes two authentication mechanisms:

1. **neptune_driver**: Uses aws-requests-auth for authentication (existing implementation)
2. **NeptuneBoto3Store**: RDFlib store subclass using boto3 with dynamic instance metadata support (new)

The plugin registers a "neptune" database driver that uses AWS SigV4 request signing for all SPARQL queries, updates, and Graph Store Protocol operations. It also extends Neptune full-text search capabilities.

## Features

- **AWS IAM Authentication**: Uses AWS SigV4 request signing for secure access to Neptune databases
- **Automatic Credential Management**: Leverages boto3 for AWS credential discovery (environment variables, IAM roles, etc.)
- **Dynamic Instance Metadata**: Automatically retrieves credentials from EC2 instance metadata when available
- **Full Text Search Support**: Passes authentication through to Neptune's full-text search queries
- **Graph Store Protocol**: Supports authenticated PUT, POST, DELETE, and publish operations
- **Configuration-Based**: Easy setup via Flask configuration

## Authentication Options

### Option 1: neptune_driver (Existing)

Uses the existing `neptune_driver` function with aws-requests-auth. Suitable for applications already using this approach.

**Dependencies**: `aws_requests_auth`

### Option 2: NeptuneBoto3Store (New - Recommended)

A new RDFlib SPARQL store subclass that uses boto3 for credential management with automatic instance metadata support. Recommended for new projects.

**Dependencies**: `boto3`, `botocore`

**See**: [NeptuneBoto3Store.md](NeptuneBoto3Store.md) for detailed documentation.

## Installation and Setup

### 1. Enable the Neptune Plugin

To enable the Neptune plugin in your Whyis knowledge graph application, add it to your application's configuration file (typically `whyis.conf` or `system.conf`):

```python
# Enable the Neptune plugin
PLUGINENGINE_PLUGINS = ['neptune']

# Or if you already have other plugins enabled:
PLUGINENGINE_PLUGINS = ['neptune', 'other_plugin']
```

### 2. Install Required Dependencies

#### For neptune_driver (Existing):

```
aws_requests_auth
```

#### For NeptuneBoto3Store (New):

```
boto3
botocore
```

Then install them in your application environment:

```bash
pip install -r requirements.txt
```

**Note**: These dependencies are only needed if you're using Neptune with IAM authentication. They are not required for core Whyis functionality.

## Configuration

After enabling the plugin and installing dependencies, configure your Whyis application to use Neptune with IAM authentication:

### System Configuration (system.conf)

```python
# Neptune SPARQL endpoint
KNOWLEDGE_TYPE = 'neptune'
KNOWLEDGE_ENDPOINT = 'https://my-cluster.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/sparql'

# AWS region (required for Neptune driver)
KNOWLEDGE_REGION = 'us-east-1'

# Optional: Custom service name (defaults to 'neptune-db')
KNOWLEDGE_SERVICE_NAME = 'neptune-db'

# Optional: Separate Graph Store Protocol endpoint
KNOWLEDGE_GSP_ENDPOINT = 'https://my-cluster.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/data'

# Optional: Default graph URI
KNOWLEDGE_DEFAULT_GRAPH = 'http://example.org/default-graph'

# Optional: Use temporary UUID graphs for GSP operations (defaults to True)
# When True, ensures graph-aware semantics for RDF data with named graphs
KNOWLEDGE_USE_TEMP_GRAPH = True

# Neptune Full-Text Search endpoint
neptune_fts_endpoint = 'https://search-my-domain.us-east-1.es.amazonaws.com'
```


### AWS Credentials

The Neptune driver uses environment variables for AWS credential management. Credentials can be provided via:

1. **Environment Variables** (required):
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_SESSION_TOKEN=your_session_token  # Optional, for temporary credentials
   ```

2. **IAM Roles**: If running on EC2 or ECS with an IAM role, set the environment variables from the role's credentials

3. **AWS Credentials File** (`~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```
   Then export them:
   ```bash
   export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
   export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
   ```

## How It Works

### Driver Registration

The Neptune plugin automatically registers a "neptune" database driver when initialized. This driver:

1. Creates Neptune SPARQL stores with AWS IAM authentication
2. Signs all HTTP requests with AWS SigV4 signatures
3. Passes authentication to full-text search queries
4. Provides authenticated Graph Store Protocol operations

### Graph-Aware Semantics with Temporary UUID Graphs

By default (when `KNOWLEDGE_USE_TEMP_GRAPH = True`), the Neptune driver ensures graph-aware semantics for all Graph Store Protocol (GSP) operations:

- **Problem**: Without this feature, Neptune's GSP implementation inserts triples into an explicit default graph (using `?default` parameter), causing all RDF data to lose its graph structure even when using graph-aware formats like TriG.

- **Solution**: The driver generates a temporary UUID-based graph URI (e.g., `urn:uuid:...`) for each GSP operation, posts/puts data to that temporary graph, and then deletes it. This ensures that:
  - Named graphs from TriG data are preserved correctly
  - Graph-aware RDF data maintains its structure
  - Union semantics are properly applied instead of explicit default graph semantics

- **Configuration**: Set `KNOWLEDGE_USE_TEMP_GRAPH = False` to disable this behavior and use legacy default graph semantics.

### Request Signing

All requests to Neptune are automatically signed with AWS SigV4:

- **SPARQL Queries**: SELECT, ASK, CONSTRUCT, DESCRIBE queries
- **SPARQL Updates**: INSERT, DELETE, MODIFY operations
- **Graph Store Protocol**: GET, PUT, POST, DELETE on named graphs
- **Full-Text Search**: Neptune FTS queries via SERVICE blocks

### Usage in SPARQL Queries

Full-text search queries work seamlessly with authentication:

```sparql
PREFIX fts: <http://aws.amazon.com/neptune/vocab/v01/services/fts#>
PREFIX dc: <http://purl.org/dc/terms/>

SELECT ?node ?label WHERE {
    SERVICE fts:search {
        fts:config neptune-fts:query "search term" .
        fts:config neptune-fts:endpoint "https://your-fts-endpoint" .
        fts:config neptune-fts:field dc:title .
        fts:config neptune-fts:return ?node .
    }
    ?node dc:title ?label .
}
```

The Neptune driver ensures that AWS credentials are attached to the full-text search requests.

## API

### Using NeptuneBoto3Store Directly (Recommended for New Projects)

For direct use of the boto3-based store with instance metadata support:

```python
from rdflib import ConjunctiveGraph
from whyis.plugins.neptune import NeptuneBoto3Store

# Create store with automatic instance metadata retrieval
store = NeptuneBoto3Store(
    query_endpoint='https://neptune.amazonaws.com:8182/sparql',
    update_endpoint='https://neptune.amazonaws.com:8182/sparql',
    region_name='us-east-1'
)

# Create graph
graph = ConjunctiveGraph(store)

# Use the graph for SPARQL operations
results = graph.query("""
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
    } LIMIT 10
""")
```

**Key Features**:
- Automatic credential retrieval from EC2 instance metadata
- Fallback to boto3 session credentials
- Dynamic credential refresh
- No explicit credential configuration needed on EC2

See [NeptuneBoto3Store.md](NeptuneBoto3Store.md) for complete documentation.

### Neptune Driver Function (Existing)

```python
from whyis.plugins.neptune.plugin import neptune_driver

config = {
    '_endpoint': 'https://neptune.amazonaws.com:8182/sparql',
    '_region': 'us-east-1',
    '_service_name': 'neptune-db',  # Optional
    '_gsp_endpoint': 'https://neptune.amazonaws.com:8182/data',  # Optional
    '_default_graph': 'http://example.org/graph'  # Optional
}

graph = neptune_driver(config)
```

## Security Considerations

- **Credentials**: Never commit AWS credentials to source control
- **IAM Policies**: Ensure Neptune IAM policies grant only necessary permissions
- **Temporary Credentials**: Use STS temporary credentials or IAM roles when possible
- **HTTPS**: Always use HTTPS endpoints for Neptune
- **VPC**: Consider using VPC endpoints for Neptune access within AWS

## Troubleshooting

### Authentication Errors

If you see authentication errors:

1. Verify AWS credentials are properly configured
2. Check that the IAM policy grants Neptune access:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "neptune-db:connect",
       "neptune-db:ReadDataViaQuery",
       "neptune-db:WriteDataViaQuery"
     ],
     "Resource": "arn:aws:neptune-db:region:account:cluster-id/*"
   }
   ```
3. Ensure the region is correctly specified
4. Verify the Neptune endpoint URL is correct

### Connection Errors

If you cannot connect to Neptune:

1. Check VPC security groups allow access
2. Verify network connectivity to Neptune endpoint
3. Ensure the endpoint URL includes the port (typically 8182)
4. Check that Neptune cluster is available

## References

- [AWS Neptune IAM Authentication](https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth.html)
- [AWS Neptune Full-Text Search](https://docs.aws.amazon.com/neptune/latest/userguide/full-text-search.html)
- [AWS SigV4 Signing](https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html)
- [boto3 Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
