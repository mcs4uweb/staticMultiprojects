import boto3
import json
import os
import sys


# =============================================================================
# AWS Bedrock Configuration
# =============================================================================
# AIDEV-NOTE: This script uses boto3 to interact with AWS Bedrock.
# Ensure you have the boto3 library installed: pip install boto3
# Your AWS credentials must be configured (via `aws configure` or environment variables).
# You must also have access to the Bedrock service in your AWS account.

# AIDEV-NOTE: Initialize the Bedrock client.
# The `region_name` should be a region where Bedrock is available, such as 'us-east-1'.
aws_region = os.getenv("AWS_REGION", "us-east-1")

try:
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=aws_region,
    )
except Exception as e:
    print(f"Error creating AWS Bedrock client: {e}")
    sys.exit(1)

def invoke_bedrock_model(model_id, prompt):
    """
    Invokes a specified Bedrock model with a given prompt.

    Args:
        model_id (str): The ID of the model to invoke (e.g., 'anthropic.claude-v2').
        prompt (str): The text prompt for the model.

    Returns:
        str: The generated text from the model, or None on error.
    """
    print(f"Invoking model '{model_id}' with prompt: '{prompt}'")
    
    # AIDEV-NOTE: The payload structure is specific to each model.
    # This example uses the format for Anthropic's Claude models.
    # For other models like Titan, the keys and values will be different.
    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 1024,
        "temperature": 0.5,
        "top_p": 0.9
    })
    
    try:
        # AIDEV-NOTE: Call the Bedrock service using the invoke_model API.
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        # AIDEV-NOTE: The response is a stream of bytes, so we read it and parse the JSON.
        response_body = json.loads(response.get('body').read())
        
        # AIDEV-NOTE: Extract the generated text from the response.
        # The key 'completion' is specific to Anthropic models.
        completion = response_body.get('completion')
        return completion
        
    except Exception as e:
        print(f"Error invoking Bedrock model: {e}")
        return None

if __name__ == "__main__":
    # =============================================================================
    # User-defined variables - EDIT THESE
    # =============================================================================
    # AIDEV-NOTE: Replace with your desired model and prompt.
    # You need to have access to this model in your AWS account.
    MODEL_ID = 'anthropic.claude-opus-4-1-20250805-v1:0'
    USER_PROMPT = "Write a short poem about a rainy day."

    # AIDEV-NOTE: The script will call the main function with your details.
    generated_text = invoke_bedrock_model(MODEL_ID, USER_PROMPT)

    # AIDEV-NOTE: Check if the invocation was successful before printing.
    if generated_text:
        print("\n--- Generated Text ---")
        print(generated_text)
