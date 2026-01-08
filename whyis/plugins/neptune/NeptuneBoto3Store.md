# NeptuneBoto3Store

A subclass of RDFlib's `SPARQLUpdateStore` that uses boto3 for AWS Neptune authentication with dynamic credential retrieval from EC2 instance metadata.

## Overview

`NeptuneBoto3Store` extends `WhyisSPARQLUpdateStore` to provide robust AWS authentication for Amazon Neptune databases. It leverages boto3's credential management system and supports dynamic credential retrieval from EC2 instance metadata via `InstanceMetadataProvider` and `InstanceMetadataFetcher`.

## Features

- **boto3 Credential Management**: Uses boto3's full credential chain (environment variables, credential files, IAM roles)
- **Dynamic Instance Metadata Retrieval**: Automatically fetches credentials from EC2 instance metadata service when running on EC2
- **AWS SigV4 Request Signing**: All HTTP requests are signed with AWS SigV4 signatures
- **Automatic Credential Refresh**: Credentials are dynamically retrieved for each request, ensuring they're always current
- **Fallback Mechanism**: Falls back to boto3 session credentials if instance metadata is unavailable
- **RDFlib Compatible**: Works seamlessly with RDFlib's `ConjunctiveGraph`

## Installation

Install the required dependencies:

```bash
pip install boto3 botocore
```

## Usage

### Basic Usage

```python
from rdflib import ConjunctiveGraph
from whyis.plugins.neptune import NeptuneBoto3Store

# Create the store
store = NeptuneBoto3Store(
    query_endpoint='https://my-neptune.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/sparql',
    update_endpoint='https://my-neptune.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/sparql',
    region_name='us-east-1'
)

# Create a graph with the store
graph = ConjunctiveGraph(store)

# Use the graph for SPARQL operations
results = graph.query("""
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    LIMIT 10
""")
```

### Advanced Configuration

```python
import boto3
from whyis.plugins.neptune import NeptuneBoto3Store

# Use a custom boto3 session
session = boto3.Session(
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET',
    region_name='us-east-1'
)

store = NeptuneBoto3Store(
    query_endpoint='https://neptune.amazonaws.com:8182/sparql',
    update_endpoint='https://neptune.amazonaws.com:8182/sparql',
    region_name='us-east-1',
    service_name='neptune-db',  # Custom service name
    boto3_session=session,  # Use custom session
    use_instance_metadata=True  # Enable instance metadata (default)
)
```

### Disabling Instance Metadata

If you don't want to use instance metadata and prefer only boto3 session credentials:

```python
store = NeptuneBoto3Store(
    query_endpoint='https://neptune.amazonaws.com:8182/sparql',
    update_endpoint='https://neptune.amazonaws.com:8182/sparql',
    region_name='us-east-1',
    use_instance_metadata=False  # Disable instance metadata
)
```

## Credential Retrieval

`NeptuneBoto3Store` retrieves credentials in the following order:

1. **Instance Metadata Provider** (if `use_instance_metadata=True`):
   - Uses `InstanceMetadataFetcher` to fetch credentials from EC2 instance metadata service
   - Automatically used when running on EC2 with an IAM role
   - Credentials are dynamically refreshed

2. **boto3 Session Credentials** (fallback):
   - Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`)
   - AWS credentials file (`~/.aws/credentials`)
   - IAM roles (when running on EC2/ECS/Lambda)

## Parameters

### `__init__` Parameters

- **`query_endpoint`** (str, required): SPARQL query endpoint URL
- **`update_endpoint`** (str, required): SPARQL update endpoint URL
- **`region_name`** (str, required): AWS region where Neptune is located
- **`service_name`** (str, optional): AWS service name for signing (default: `'neptune-db'`)
- **`boto3_session`** (boto3.Session, optional): Custom boto3 session. If not provided, a new session is created.
- **`use_instance_metadata`** (bool, optional): Enable dynamic credential retrieval from EC2 instance metadata (default: `True`)
- **`**kwargs`**: Additional arguments passed to `WhyisSPARQLUpdateStore`

## Methods

### `_get_credentials()`

Dynamically retrieves current AWS credentials, prioritizing instance metadata when available.

**Returns**: Frozen credentials object with `access_key`, `secret_key`, and `token` attributes.

### `_sign_request(method, url, headers=None, body=None)`

Signs an HTTP request using AWS SigV4 with dynamically retrieved credentials.

**Parameters**:
- `method` (str): HTTP method (GET, POST, etc.)
- `url` (str): Full URL including query parameters
- `headers` (dict): HTTP headers
- `body`: Request body (str or bytes)

**Returns**: Dictionary of signed headers including AWS signature.

### `_request(method, url, headers=None, body=None)`

Makes an authenticated HTTP request to Neptune.

**Returns**: Response object from requests library.

## EC2 Instance Metadata

When running on EC2 instances with IAM roles, `NeptuneBoto3Store` automatically:

1. Discovers the IAM role attached to the instance
2. Fetches temporary credentials from the instance metadata service
3. Refreshes credentials automatically when they expire
4. Falls back to other credential sources if metadata is unavailable

This is ideal for production deployments where you want to avoid managing long-lived credentials.

## Example: Running on EC2

```python
# When running on an EC2 instance with an IAM role,
# no credential configuration is needed!
from rdflib import ConjunctiveGraph
from whyis.plugins.neptune import NeptuneBoto3Store

store = NeptuneBoto3Store(
    query_endpoint='https://neptune.amazonaws.com:8182/sparql',
    update_endpoint='https://neptune.amazonaws.com:8182/sparql',
    region_name='us-east-1'
    # Credentials will be automatically retrieved from instance metadata
)

graph = ConjunctiveGraph(store)
# Use the graph...
```

## Comparison with Existing Neptune Driver

The Neptune plugin includes two authentication mechanisms:

### 1. `neptune_driver` (Existing)
- Uses `aws-requests-auth` library
- Requires explicit AWS credentials in environment variables
- Uses `WhyisSPARQLUpdateStore` with custom requests session

### 2. `NeptuneBoto3Store` (New)
- Uses boto3's comprehensive credential management
- Supports dynamic instance metadata retrieval
- Better integration with AWS SDK patterns
- Automatic credential refresh
- Recommended for new projects

## Security Considerations

- **No Hardcoded Credentials**: Never hardcode AWS credentials in your code
- **IAM Roles**: Use IAM roles when possible (EC2, ECS, Lambda)
- **Temporary Credentials**: Instance metadata provides temporary, auto-rotating credentials
- **Least Privilege**: Ensure IAM policies grant only necessary permissions
- **HTTPS Only**: Always use HTTPS endpoints for Neptune

## IAM Policy Example

Your IAM role or user should have permissions like:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "neptune-db:connect",
        "neptune-db:ReadDataViaQuery",
        "neptune-db:WriteDataViaQuery"
      ],
      "Resource": "arn:aws:neptune-db:region:account-id:cluster-id/*"
    }
  ]
}
```

## Error Handling

The store raises appropriate errors for common issues:

```python
# Missing region
try:
    store = NeptuneBoto3Store(
        query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://neptune.amazonaws.com:8182/sparql'
    )
except ValueError as e:
    print(f"Error: {e}")  # "region_name is required for NeptuneBoto3Store"

# No credentials available
try:
    store = NeptuneBoto3Store(
        query_endpoint='https://neptune.amazonaws.com:8182/sparql',
        update_endpoint='https://neptune.amazonaws.com:8182/sparql',
        region_name='us-east-1',
        use_instance_metadata=False
    )
except ValueError as e:
    print(f"Error: {e}")  # "No AWS credentials found..."
```

## Testing

The implementation includes comprehensive unit tests. Run them with:

```bash
pytest tests/unit/test_neptune_boto3_store.py -v
```

Test coverage includes:
- Initialization with various configurations
- Instance metadata provider setup
- Dynamic credential retrieval
- Request signing with different credential types
- Integration with RDFlib
- Error handling

## References

- [AWS Neptune IAM Authentication](https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth.html)
- [boto3 Credentials Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [EC2 Instance Metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)
- [AWS SigV4 Signing](https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html)
- [RDFlib Documentation](https://rdflib.readthedocs.io/)
