import boto3

# Replace with the actual ID from the setup script output
KNOWLEDGE_BASE_ID = 'YOUR_KNOWLEDGE_BASE_ID'
REGION = 'us-gov-west-1'

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)

query = "What is the capital of France?"

try:
    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 3  # The number of relevant chunks to retrieve
            }
        }
    )

    print("Retrieved Results:")
    for result in response['retrievalResults']:
        content = result['content']['text']
        print(f"Content: {content}\n---")

except Exception as e:
    print(f"An error occurred: {e}")