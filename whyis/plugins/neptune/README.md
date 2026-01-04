# Neptune Plugin - AWS IAM Authentication Support

## Overview

This plugin extends the Neptune full-text search capabilities to include AWS IAM authentication support for Amazon Neptune databases. It registers a "neptune" database driver that uses AWS SigV4 request signing for all SPARQL queries, updates, and Graph Store Protocol operations.

## Features

- **AWS IAM Authentication**: Uses AWS SigV4 request signing for secure access to Neptune databases
- **Automatic Credential Management**: Leverages boto3 for AWS credential discovery (environment variables, IAM roles, etc.)
- **Full Text Search Support**: Passes authentication through to Neptune's full-text search queries
- **Graph Store Protocol**: Supports authenticated PUT, POST, DELETE, and publish operations
- **Configuration-Based**: Easy setup via Flask configuration

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

The Neptune plugin with IAM authentication requires additional Python packages that are not included in the core Whyis dependencies. Add these to your knowledge graph application's `requirements.txt`:

```
boto3
requests-aws4auth
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

# Neptune Full-Text Search endpoint
neptune_fts_endpoint = 'https://search-my-domain.us-east-1.es.amazonaws.com'
```

### AWS Credentials

The Neptune driver uses boto3 for AWS credential management. Credentials can be provided via:

1. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_SESSION_TOKEN=your_session_token  # Optional, for temporary credentials
   ```

2. **IAM Roles**: If running on EC2 or ECS, the driver will automatically use the instance/task IAM role

3. **AWS Credentials File** (`~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```

4. **AWS Config File** (`~/.aws/config`):
   ```ini
   [default]
   region = us-east-1
   ```

## How It Works

### Driver Registration

The Neptune plugin automatically registers a "neptune" database driver when initialized. This driver:

1. Creates Neptune SPARQL stores with AWS IAM authentication
2. Signs all HTTP requests with AWS SigV4 signatures
3. Passes authentication to full-text search queries
4. Provides authenticated Graph Store Protocol operations

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

### Neptune Driver Function

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

### Neptune Query Store

```python
from whyis.plugins.neptune.plugin import create_neptune_query_store

# Create a read-only query store from an existing Neptune store
query_store = create_neptune_query_store(existing_store)
```

### Neptune SPARQL Stores

```python
from whyis.plugins.neptune.neptune_sparql_store import (
    NeptuneSPARQLStore,
    NeptuneSPARQLUpdateStore,
    NeptuneSPARQLConnector
)

# Create a Neptune store with IAM authentication
store = NeptuneSPARQLUpdateStore(
    query_endpoint='https://neptune.amazonaws.com:8182/sparql',
    update_endpoint='https://neptune.amazonaws.com:8182/sparql',
    region_name='us-east-1',
    service_name='neptune-db'
)
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
