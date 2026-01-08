# Setting Up AWS Neptune with CloudFormation

This directory contains a CloudFormation template (`cloudformation-neptune.json`) that automates the deployment of AWS Neptune Serverless with Full-Text Search capabilities for your Whyis knowledge graph application.

## What This Template Creates

The CloudFormation template provisions:

1. **Neptune Serverless Cluster**: A scalable Neptune database cluster with IAM authentication enabled
2. **OpenSearch Domain**: For full-text search capabilities integrated with Neptune
3. **Security Groups**: Proper network security for both Neptune and OpenSearch
4. **IAM Role**: With necessary permissions to access both Neptune and OpenSearch
5. **VPC Configuration**: Subnet groups for secure deployment

## Prerequisites

Before deploying this template, you need:

1. **AWS Account** with appropriate permissions to create:
   - Neptune clusters
   - OpenSearch domains
   - IAM roles and policies
   - EC2 security groups
   - VPC subnet groups

2. **Existing VPC** with:
   - At least 2 private subnets in different Availability Zones
   - Proper routing configuration
   - NAT Gateway (if your application needs internet access)

3. **AWS CLI** installed and configured (or use AWS Console)

## Deployment Steps

### Option 1: Using AWS CLI

1. **Prepare your parameters** by creating a `parameters.json` file:

```json
[
  {
    "ParameterKey": "DBClusterIdentifier",
    "ParameterValue": "my-kgapp-neptune"
  },
  {
    "ParameterKey": "VPCId",
    "ParameterValue": "vpc-xxxxxxxxx"
  },
  {
    "ParameterKey": "PrivateSubnetIds",
    "ParameterValue": "subnet-xxxxxxxx,subnet-yyyyyyyy"
  },
  {
    "ParameterKey": "AllowedCIDR",
    "ParameterValue": "10.0.0.0/16"
  },
  {
    "ParameterKey": "IAMRoleName",
    "ParameterValue": "my-kgapp-neptune-access"
  },
  {
    "ParameterKey": "MinNCUs",
    "ParameterValue": "2.5"
  },
  {
    "ParameterKey": "MaxNCUs",
    "ParameterValue": "128"
  },
  {
    "ParameterKey": "OpenSearchInstanceType",
    "ParameterValue": "t3.small.search"
  },
  {
    "ParameterKey": "OpenSearchInstanceCount",
    "ParameterValue": "1"
  }
]
```

2. **Deploy the stack**:

```bash
aws cloudformation create-stack \
  --stack-name my-kgapp-neptune-stack \
  --template-body file://cloudformation-neptune.json \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

3. **Monitor the deployment**:

```bash
aws cloudformation describe-stacks \
  --stack-name my-kgapp-neptune-stack \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus'
```

The deployment typically takes 20-30 minutes to complete.

4. **Get the outputs**:

```bash
aws cloudformation describe-stacks \
  --stack-name my-kgapp-neptune-stack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

### Option 2: Using AWS Console

1. Log into the AWS Console
2. Navigate to CloudFormation service
3. Click "Create Stack" → "With new resources"
4. Select "Upload a template file"
5. Upload the `cloudformation-neptune.json` file
6. Fill in the required parameters:
   - **DBClusterIdentifier**: Unique name for your Neptune cluster
   - **VPCId**: Select your VPC
   - **PrivateSubnetIds**: Select at least 2 private subnets in different AZs
   - **AllowedCIDR**: IP range that can access Neptune and OpenSearch
   - **IAMRoleName**: Name for the IAM role (must be unique)
   - **MinNCUs/MaxNCUs**: Capacity settings for Neptune Serverless
   - **OpenSearchInstanceType**: Instance type for OpenSearch
   - **OpenSearchInstanceCount**: Number of OpenSearch nodes
7. Acknowledge IAM resource creation
8. Click "Create Stack"

## Configuring Your Whyis Application

After the CloudFormation stack completes, configure your Whyis application:

### 1. Get Configuration Values from Stack Outputs

The CloudFormation outputs provide all the values you need. Key outputs:

- `NeptuneSPARQLEndpoint`: Neptune SPARQL endpoint URL
- `OpenSearchFTSEndpoint`: OpenSearch full-text search endpoint
- `Region`: AWS region
- `NeptuneAccessRoleArn`: IAM role ARN for accessing Neptune
- `WhyisConfigSummary`: Quick reference of all configuration values

### 2. Update whyis.conf

Add these lines to your `whyis.conf`:

```python
# Enable Neptune plugin
PLUGINENGINE_PLUGINS = ['neptune']

# Neptune configuration
KNOWLEDGE_TYPE = 'neptune'
KNOWLEDGE_ENDPOINT = 'https://<neptune-endpoint>:8182/sparql'  # From NeptuneSPARQLEndpoint output
KNOWLEDGE_REGION = 'us-east-1'  # From Region output

# Full-text search configuration
neptune_fts_endpoint = 'https://<opensearch-endpoint>'  # From OpenSearchFTSEndpoint output
```

### 3. Add Dependencies to requirements.txt

```
aws_requests_auth
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

Your application needs AWS credentials to access Neptune. Choose one option:

#### Option A: Using IAM Role (Recommended for EC2/ECS)

If running on EC2, attach the instance profile to your instance:

```bash
# Get the instance profile ARN from CloudFormation outputs
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxxxxxx \
  --iam-instance-profile Arn=<NeptuneAccessInstanceProfileArn>
```

#### Option B: Using Environment Variables (For local development)

Create an IAM user with permissions to assume the Neptune access role, then:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

#### Option C: Using AWS CLI Profile

```bash
aws configure --profile neptune
# Enter your credentials
export AWS_PROFILE=neptune
```

### 5. Verify the Configuration

Start your Whyis application and verify Neptune connection:

```bash
./run
```

Check the logs for successful Neptune plugin initialization and database connection.

## Configuration Parameters Explained

### Required Parameters

- **DBClusterIdentifier**: Unique identifier for your Neptune cluster (3-63 characters, alphanumeric and hyphens)
- **VPCId**: The VPC where Neptune and OpenSearch will be deployed
- **PrivateSubnetIds**: At least 2 private subnets in different Availability Zones for high availability
- **AllowedCIDR**: CIDR block that can access Neptune and OpenSearch (e.g., your VPC CIDR)
- **IAMRoleName**: Name for the IAM role that grants access to Neptune and OpenSearch

### Optional Parameters (with defaults)

- **MinNCUs**: Minimum Neptune Capacity Units (default: 2.5) - Lowest cost option
- **MaxNCUs**: Maximum Neptune Capacity Units (default: 128) - Allows scaling to high workloads
- **OpenSearchInstanceType**: Instance type for OpenSearch (default: t3.small.search) - Good for development
- **OpenSearchInstanceCount**: Number of OpenSearch instances (default: 1) - Use 2+ for production

## Cost Considerations

### Neptune Serverless Costs

- **NCU-hours**: Charged per NCU-hour when cluster is active
- **Storage**: Charged per GB-month
- **I/O**: Charged per million requests
- **Backups**: Automated backups included, additional snapshots charged

Estimated monthly cost (with 2.5 NCUs average, 10GB data):
- ~$150-300/month depending on usage patterns

### OpenSearch Costs

- **Instance hours**: Based on instance type (t3.small.search ~$35/month)
- **Storage**: Charged per GB (20GB included in template)

### Cost Optimization Tips

1. **Development**: Use MinNCUs=1, t3.small.search, single instance
2. **Production**: Use MinNCUs=2.5, larger instance types, multiple instances for HA
3. **Stop when not in use**: Neptune Serverless automatically scales to zero after inactivity
4. **Monitor usage**: Use AWS Cost Explorer to track actual costs

## Security Best Practices

1. **Network Security**:
   - Deploy in private subnets only
   - Use restrictive security groups
   - Set AllowedCIDR to minimum required range

2. **IAM Authentication**:
   - Always use IAM authentication (enabled by default in template)
   - Rotate credentials regularly
   - Use IAM roles instead of long-term credentials when possible

3. **Encryption**:
   - Encryption at rest enabled by default
   - TLS/HTTPS enforced for all connections
   - Node-to-node encryption enabled for OpenSearch

4. **Least Privilege**:
   - Use the provided IAM role with minimal permissions
   - Create separate roles for different access patterns if needed

## Troubleshooting

### Stack Creation Failed

1. **Check CloudFormation Events**: 
   ```bash
   aws cloudformation describe-stack-events \
     --stack-name my-kgapp-neptune-stack \
     --region us-east-1
   ```

2. **Common Issues**:
   - Insufficient IAM permissions
   - VPC/Subnet configuration issues
   - Resource naming conflicts
   - Service limits exceeded

### Connection Issues

1. **Verify Security Groups**: Ensure your application's security group can reach Neptune (port 8182) and OpenSearch (port 443)

2. **Check IAM Permissions**: Verify the IAM role has neptune-db:* and es:* permissions

3. **Test Connectivity**:
   ```bash
   # From an instance in the same VPC
   curl -k https://<neptune-endpoint>:8182/sparql
   ```

### OpenSearch Access Issues

1. **Fine-grained Access Control**: Ensure the IAM role ARN is configured as master user
2. **VPC Configuration**: Verify OpenSearch is in the correct subnets
3. **Domain Policy**: Check the access policy allows your CIDR range

## Updating the Stack

To update configuration (e.g., increase capacity):

```bash
aws cloudformation update-stack \
  --stack-name my-kgapp-neptune-stack \
  --template-body file://cloudformation-neptune.json \
  --parameters file://updated-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

## Deleting the Stack

To remove all resources:

```bash
aws cloudformation delete-stack \
  --stack-name my-kgapp-neptune-stack \
  --region us-east-1
```

**Warning**: This will permanently delete:
- All data in Neptune
- All data in OpenSearch
- Security groups and IAM roles

Create a backup before deletion if you need to preserve data.

## Additional Resources

- [AWS Neptune Documentation](https://docs.aws.amazon.com/neptune/latest/userguide/)
- [Neptune IAM Authentication](https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth.html)
- [Neptune Full-Text Search](https://docs.aws.amazon.com/neptune/latest/userguide/full-text-search.html)
- [OpenSearch Documentation](https://docs.aws.amazon.com/opensearch-service/)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
