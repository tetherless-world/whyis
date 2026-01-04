.. _neptune-iam-auth:

Using Neptune with AWS IAM Authentication
==========================================

This guide explains how to configure your Whyis knowledge graph application to use Amazon Neptune with AWS IAM authentication.

Overview
--------

The Neptune plugin extends Whyis to support AWS IAM authentication for Amazon Neptune databases. It uses AWS SigV4 request signing for all SPARQL operations, including:

- SPARQL queries (SELECT, ASK, CONSTRUCT, DESCRIBE)
- SPARQL updates (INSERT, DELETE, MODIFY)
- Graph Store Protocol operations (PUT, POST, DELETE)
- Full-text search queries via Neptune FTS

Prerequisites
-------------

- A Whyis knowledge graph application (created with ``whyis createapp``)
- Access to an Amazon Neptune database cluster
- AWS credentials with Neptune access permissions

Step 1: Enable the Neptune Plugin
----------------------------------

Add the Neptune plugin to your application's configuration file (``whyis.conf`` or ``system.conf``):

.. code-block:: python

    # Enable the Neptune plugin
    PLUGINENGINE_PLUGINS = ['neptune']
    
    # Or if you already have other plugins enabled:
    PLUGINENGINE_PLUGINS = ['neptune', 'other_plugin']

Step 2: Install Required Dependencies
--------------------------------------

The Neptune plugin requires additional Python packages that are **not** included in core Whyis. 

Add these packages to your application's ``requirements.txt``:

.. code-block:: text

    boto3
    requests-aws4auth

Then install them in your application environment:

.. code-block:: bash

    pip install -r requirements.txt

.. note::
    These dependencies are only needed when using Neptune with IAM authentication. They are not required for core Whyis functionality or other database backends.

Step 3: Configure Neptune Connection
-------------------------------------

Add Neptune configuration to your application's ``whyis.conf`` or ``system.conf``:

.. code-block:: python

    # Configure Neptune as the knowledge database
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
    
    # Neptune Full-Text Search endpoint (if using FTS)
    neptune_fts_endpoint = 'https://search-my-domain.us-east-1.es.amazonaws.com'

.. important::
    Replace the endpoint URLs with your actual Neptune cluster endpoints.

Step 4: Configure AWS Credentials
----------------------------------

The Neptune driver uses ``boto3`` for AWS credential management. Credentials can be provided in several ways:

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    export AWS_ACCESS_KEY_ID=your_access_key
    export AWS_SECRET_ACCESS_KEY=your_secret_key
    export AWS_SESSION_TOKEN=your_session_token  # Optional, for temporary credentials

IAM Roles (Recommended for EC2/ECS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your Whyis application runs on EC2 or ECS, the driver will automatically use the instance or task IAM role. This is the recommended approach as it avoids managing credentials directly.

AWS Credentials File
~~~~~~~~~~~~~~~~~~~~

Create or edit ``~/.aws/credentials``:

.. code-block:: ini

    [default]
    aws_access_key_id = your_access_key
    aws_secret_access_key = your_secret_key

And ``~/.aws/config``:

.. code-block:: ini

    [default]
    region = us-east-1

Step 5: Configure IAM Permissions
----------------------------------

Ensure your AWS credentials or IAM role have the necessary Neptune permissions. Example IAM policy:

.. code-block:: json

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
          "Resource": "arn:aws:neptune-db:us-east-1:123456789012:cluster-XXXXX/*"
        }
      ]
    }

Step 6: Verify the Configuration
---------------------------------

Start your Whyis application and verify the Neptune connection:

.. code-block:: bash

    cd /apps/your-app
    ./run

Check the application logs for successful Neptune driver registration and database connection.

How It Works
------------

Request Signing
~~~~~~~~~~~~~~~

All HTTP requests to Neptune are automatically signed with AWS SigV4:

- The Neptune connector creates a ``requests.Session`` with ``AWS4Auth``
- AWS credentials are fetched via ``boto3.Session().get_credentials()``
- Each request includes signed headers for authentication
- Credentials are automatically refreshed when using IAM roles

Full-Text Search Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Full-text search queries work seamlessly with authentication:

.. code-block:: sparql

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

The Neptune driver ensures AWS credentials are attached to full-text search requests.

Troubleshooting
---------------

Authentication Errors
~~~~~~~~~~~~~~~~~~~~~

If you encounter authentication errors:

1. Verify AWS credentials are properly configured
2. Check IAM policy grants Neptune access (see Step 5)
3. Ensure the region matches your Neptune cluster
4. Verify the Neptune endpoint URL is correct

Connection Errors
~~~~~~~~~~~~~~~~~

If you cannot connect to Neptune:

1. Check VPC security groups allow access from your application
2. Verify network connectivity to Neptune endpoint
3. Ensure the endpoint URL includes the port (typically 8182)
4. Verify your Neptune cluster is available

Import Errors
~~~~~~~~~~~~~

If you see ``ModuleNotFoundError: No module named 'boto3'`` or similar:

1. Ensure ``boto3`` and ``requests-aws4auth`` are in your application's ``requirements.txt``
2. Run ``pip install -r requirements.txt`` in your application environment
3. Restart your application

Security Considerations
-----------------------

- **Never commit AWS credentials to source control**
- Use IAM roles when running on AWS infrastructure (EC2, ECS, Lambda)
- Use temporary credentials (STS) when possible
- Always use HTTPS endpoints for Neptune connections
- Restrict IAM policies to minimum required permissions
- Consider using VPC endpoints for Neptune access within AWS

Additional Resources
--------------------

- `AWS Neptune IAM Authentication <https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth.html>`_
- `AWS Neptune Full-Text Search <https://docs.aws.amazon.com/neptune/latest/userguide/full-text-search.html>`_
- `AWS SigV4 Signing <https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html>`_
- `boto3 Credentials <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_
