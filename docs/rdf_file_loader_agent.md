# RDF File Loader Agent

## Overview

The RDF File Loader agent automatically loads RDF files into the Whyis knowledge graph as nanopublications. It monitors resources typed as `whyis:RDFFile` and loads their content.

## Features

- **Multiple Source Support:**
  - Local files from the file depot (via `whyis:hasFileID`)
  - Remote HTTP/HTTPS URLs
  - S3 URIs (requires boto3 to be installed)

- **Format Detection:**
  - Automatic format detection from file extensions and content types
  - Supports: Turtle (.ttl), RDF/XML (.rdf, .owl), JSON-LD (.jsonld), N-Triples (.nt), N3 (.n3), TriG (.trig), N-Quads (.nq)

- **Provenance Tracking:**
  - Resources are marked with `whyis:RDFFile` type before processing
  - After loading, marked as `whyis:LoadedRDFFile`
  - Activities are tracked as `whyis:RDFFileLoadingActivity`
  - Proper nanopublication structure with provenance

## Usage

### 1. Add the agent to your configuration

In your application's config file:

```python
from whyis import autonomic

class Config:
    INFERENCERS = {
        'RDFFileLoader': autonomic.RDFFileLoader(),
        # ... other agents
    }
```

### 2. Mark resources as RDF files

Create a nanopublication that types a resource as `whyis:RDFFile`:

```turtle
@prefix whyis: <http://vocab.rpi.edu/whyis/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://example.com/my-data-file> a whyis:RDFFile .
```

### 3. Loading from different sources

#### Local File Depot

For files already uploaded to the file depot:

```turtle
<http://example.com/my-file> a whyis:RDFFile ;
    whyis:hasFileID "file_depot_id_here" .
```

#### HTTP/HTTPS URL

Simply use the URL as the resource URI:

```turtle
<http://example.com/data/dataset.ttl> a whyis:RDFFile .
```

or

```turtle
<https://secure.example.com/rdf/ontology.owl> a whyis:RDFFile .
```

#### S3 URI

For files stored in S3 (requires boto3):

```turtle
<s3://my-bucket/path/to/data.ttl> a whyis:RDFFile .
```

**Note:** Ensure boto3 is installed and AWS credentials are configured:
```bash
pip install boto3
```

AWS credentials can be configured via:
- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- AWS credentials file (~/.aws/credentials)
- IAM role (when running on EC2)

## How It Works

1. The agent queries for resources typed as `whyis:RDFFile` that are not yet `whyis:LoadedRDFFile`
2. For each resource:
   - Checks if it has a `whyis:hasFileID` (file depot)
   - Otherwise, examines the URI scheme (http://, https://, s3://)
   - Downloads and parses the RDF content
   - Adds the loaded triples to a nanopublication
   - Marks the resource as `whyis:LoadedRDFFile`
3. The nanopublication includes provenance linking back to the source file

## Retirement

When a resource is no longer typed as `whyis:RDFFile`, the agent's update mechanism will retire the associated nanopublications containing the loaded data.

## Testing

The agent includes 26 comprehensive unit tests covering:
- Basic functionality
- Format detection
- HTTP/HTTPS loading
- S3 loading (with and without boto3)
- File depot access
- Error handling

Run tests with:
```bash
pytest tests/unit/test_rdf_file_loader*.py
```

## Error Handling

- **Missing boto3:** Gracefully fails with a clear error message when trying to load from S3
- **Invalid RDF:** Logs errors when content cannot be parsed
- **Network errors:** Propagates HTTP errors with proper logging
- **Missing files:** Reports file depot access errors

## Example Use Cases

1. **Bulk Data Import:** Mark multiple HTTP URLs as RDFFile to automatically import external datasets
2. **S3 Data Pipeline:** Load RDF files from S3 buckets as part of a data processing pipeline
3. **File Upload Processing:** When users upload RDF files, mark them as RDFFile for automatic processing
4. **Ontology Loading:** Automatically load and update ontologies from remote URLs
