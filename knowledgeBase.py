import boto3
import json
import time

# --- Configuration ---
# Update these variables with your own values
REGION = 'us-east-1'
KNOWLEDGE_BASE_NAME = 'MyBedrockKnowledgeBase'
VECTOR_STORE_NAME = 'my-knowledge-base-vector-store'
S3_BUCKET_NAME = 'your-unique-s3-bucket-name'
DATA_SOURCE_NAME = 'MyS3DataSource'
OPEN_SEARCH_COLLECTION_NAME = 'my-bedrock-collection'

# --- IAM Role and Policy Names ---
BEDROCK_SERVICE_ROLE_NAME = f'{KNOWLEDGE_BASE_NAME}-ServiceRole'
BEDROCK_KNOWLEDGE_BASE_POLICY_NAME = f'{KNOWLEDGE_BASE_NAME}-ServicePolicy'
OPEN_SEARCH_ENCRYPTION_POLICY_NAME = f'{OPEN_SEARCH_COLLECTION_NAME}-encryption-policy'
OPEN_SEARCH_NETWORK_POLICY_NAME = f'{OPEN_SEARCH_COLLECTION_NAME}-network-policy'
OPEN_SEARCH_ACCESS_POLICY_NAME = f'{OPEN_SEARCH_COLLECTION_NAME}-access-policy'

# Initialize boto3 clients
iam_client = boto3.client('iam', region_name=REGION)
bedrock_agent_client = boto3.client('bedrock-agent', region_name=REGION)
opensearch_serverless_client = boto3.client('opensearchserverless', region_name=REGION)

def create_iam_role_and_policy():
    """
    Creates an IAM service role for the Bedrock Knowledge Base.
    """
    print("Creating IAM role and policy for Bedrock service...")

    # Define the trust policy
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        # Create the role
        role_response = iam_client.create_role(
            RoleName=BEDROCK_SERVICE_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Amazon Bedrock Knowledge Base to access resources.'
        )
        role_arn = role_response['Role']['Arn']
        print(f"Created role: {role_arn}")

        # Define the inline policy for S3 and OpenSearch access
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{S3_BUCKET_NAME}",
                        f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": "bedrock:InvokeModel",
                    "Resource": "arn:aws:bedrock:*:*:foundation-model/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "aoss:APIAccessAll"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        # Attach the policy to the role
        iam_client.put_role_policy(
            RoleName=BEDROCK_SERVICE_ROLE_NAME,
            PolicyName=BEDROCK_KNOWLEDGE_BASE_POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        print("Attached policy to the role.")
        return role_arn
    except Exception as e:
        print(f"Error creating IAM role or policy: {e}")
        return None

def create_opensearch_collection():
    """
    Creates a new OpenSearch Serverless collection and its access policies.
    """
    print("Creating OpenSearch Serverless collection...")
    try:
        # Create a vector store collection
        collection_response = opensearch_serverless_client.create_collection(
            name=OPEN_SEARCH_COLLECTION_NAME,
            type='VECTORSEARCH'
        )
        collection_id = collection_response['createCollectionDetail']['id']
        collection_arn = collection_response['createCollectionDetail']['arn']
        
        # Create a network policy to allow public access (for demo purposes)
        # Note: In a production environment, you should restrict this to your VPC
        network_policy = {
            "Rules": [
                {
                    "Resource": [
                        collection_arn
                    ],
                    "ResourceType": "collection",
                    "IpSource": ["0.0.0.0/0"]
                }
            ],
            "Description": "Public access for Bedrock"
        }

        opensearch_serverless_client.create_security_policy(
            name=OPEN_SEARCH_NETWORK_POLICY_NAME,
            type='network',
            policy=json.dumps(network_policy)
        )

        # Create an encryption policy
        encryption_policy = {
            "Rules": [
                {
                    "Resource": [
                        f"collection/{collection_id}"
                    ],
                    "ResourceType": "collection"
                }
            ],
            "Description": "Encryption policy for Bedrock collection",
            "AWSOwnedKey": True
        }

        opensearch_serverless_client.create_security_policy(
            name=OPEN_SEARCH_ENCRYPTION_POLICY_NAME,
            type='encryption',
            policy=json.dumps(encryption_policy)
        )
        
        print(f"OpenSearch collection '{OPEN_SEARCH_COLLECTION_NAME}' created.")
        
        # Poll for the collection to become active
        while True:
            response = opensearch_serverless_client.list_collections(collectionFilters={'name': OPEN_SEARCH_COLLECTION_NAME})
            status = response['collectionDetails'][0]['status']
            print(f"Collection status: {status}")
            if status == 'ACTIVE':
                collection_endpoint = response['collectionDetails'][0]['collectionEndpoint']
                print(f"Collection is active. Endpoint: {collection_endpoint}")
                break
            time.sleep(10)

        # Create an access policy for the Bedrock service role
        access_policy = {
            "Rules": [
                {
                    "Resource": [collection_arn],
                    "ResourceType": "collection",
                    "Permission": [
                        "aoss:ReadDocument",
                        "aoss:WriteDocument"
                    ]
                }
            ],
            "Principal": [f"arn:aws:iam::your-account-id:role/{BEDROCK_SERVICE_ROLE_NAME}"], # Replace with your account ID
            "Description": "Access policy for Bedrock service role"
        }
        opensearch_serverless_client.create_access_policy(
            name=OPEN_SEARCH_ACCESS_POLICY_NAME,
            type='data',
            policy=json.dumps(access_policy)
        )
        print("OpenSearch access policy created.")
        
        return collection_endpoint, collection_arn
        
    except Exception as e:
        print(f"Error creating OpenSearch collection: {e}")
        return None, None

def create_knowledge_base(service_role_arn, opensearch_endpoint, opensearch_arn):
    """
    Creates a Bedrock Knowledge Base and its data source.
    """
    print("Creating Bedrock Knowledge Base...")
    
    # Wait for IAM role to propagate
    time.sleep(30) 

    # Create the vector store configuration
    vector_store_config = {
        'opensearchServerlessConfiguration': {
            'collectionArn': opensearch_arn,
            'vectorIndexName': VECTOR_STORE_NAME,
            'fieldMapping': {
                'vectorField': 'vector_field',
                'textField': 'text_field',
                'metadataField': 'metadata_field'
            }
        }
    }

    try:
        # Create the knowledge base
        kb_response = bedrock_agent_client.create_knowledge_base(
            name=KNOWLEDGE_BASE_NAME,
            description='Knowledge base for my S3 data',
            roleArn=service_role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR_ENHANCED',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f'arn:aws:bedrock:{REGION}::foundation-model/amazon.titan-embed-text-v1'
                }
            },
            storageConfiguration={
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    'collectionArn': opensearch_arn,
                    'vectorIndexName': VECTOR_STORE_NAME,
                    'fieldMapping': {
                        'vectorField': 'vector_field',
                        'textField': 'text_field',
                        'metadataField': 'metadata_field'
                    }
                }
            }
        )
        knowledge_base_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"Knowledge base created with ID: {knowledge_base_id}")
        
        # Wait for the knowledge base to become active
        while True:
            response = bedrock_agent_client.get_knowledge_base(knowledgeBaseId=knowledge_base_id)
            status = response['knowledgeBase']['status']
            print(f"Knowledge base status: {status}")
            if status == 'ACTIVE':
                break
            time.sleep(10)
        
        return knowledge_base_id
    except Exception as e:
        print(f"Error creating knowledge base: {e}")
        return None

def create_data_source(knowledge_base_id):
    """
    Creates a data source for the knowledge base from an S3 bucket.
    """
    print("Creating data source from S3...")
    try:
        ds_response = bedrock_agent_client.create_data_source(
            knowledgeBaseId=knowledge_base_id,
            name=DATA_SOURCE_NAME,
            dataSourceConfiguration={
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::{S3_BUCKET_NAME}'
                }
            },
            vectorIngestionConfiguration={
                'embeddingModelArn': f'arn:aws:bedrock:{REGION}::foundation-model/amazon.titan-embed-text-v1'
            }
        )
        data_source_id = ds_response['dataSource']['dataSourceId']
        print(f"Data source created with ID: {data_source_id}")
        return data_source_id
    except Exception as e:
        print(f"Error creating data source: {e}")
        return None

def start_ingestion_job(knowledge_base_id, data_source_id):
    """
    Starts the ingestion job to process S3 data into the vector store.
    """
    print("Starting ingestion job...")
    try:
        ingestion_response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id
        )
        job_id = ingestion_response['ingestionJob']['ingestionJobId']
        print(f"Ingestion job started with ID: {job_id}")
        return job_id
    except Exception as e:
        print(f"Error starting ingestion job: {e}")
        return None

# --- Main Program Execution ---
if __name__ == "__main__":
    # Create the IAM service role for Bedrock
    service_role_arn = create_iam_role_and_policy()
    if not service_role_arn:
        print("Aborting due to IAM role creation failure.")
    else:
        # Create the OpenSearch Serverless collection
        opensearch_endpoint, opensearch_arn = create_opensearch_collection()
        if not opensearch_endpoint:
            print("Aborting due to OpenSearch collection creation failure.")
        else:
            # Create the Knowledge Base
            knowledge_base_id = create_knowledge_base(service_role_arn, opensearch_endpoint, opensearch_arn)
            if not knowledge_base_id:
                print("Aborting due to Knowledge Base creation failure.")
            else:
                # Create the data source
                data_source_id = create_data_source(knowledge_base_id)
                if not data_source_id:
                    print("Aborting due to Data Source creation failure.")
                else:
                    # Start the ingestion job
                    start_ingestion_job(knowledge_base_id, data_source_id)