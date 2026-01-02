import boto3
import json
import os

# Initialize AWS clients (configurable regions)
COMPREHEND_REGION = os.getenv('COMPREHEND_REGION', os.getenv('AWS_REGION', 'us-gov-west-1'))
BEDROCK_REGION = os.getenv('BEDROCK_REGION', os.getenv('AWS_REGION', 'us-east-1'))

comprehend_medical = boto3.client('comprehendmedical', region_name=COMPREHEND_REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)

# Sample patient note (from your example)
PATIENT_NOTE = """The patient is a 71-year-old female patient of Dr. X. The patient presented to the 
emergency room last evening with approximately 7-day to 8-day history of abdominal pain, which has 
been persistent. She has had no definite fevers or chills and no history of jaundice. The patient denies 
any significant recent weight loss."""

# Prompt template for Bedrock
PROMPT_TEMPLATE = """
You are a clinical coding assistant. Based on the patient note and the ICD-10-CM codes extracted by 
Amazon Comprehend Medical, provide a clear summary that:
1. Lists each ICD-10-CM code with its full description.
2. Cites the specific phrase(s) from the patient note that support the code.
3. Only includes codes that are clinically justified.

Patient Note:
{patient_note}

Extracted ICD-10-CM Codes (from Comprehend Medical):
{icd10_codes}

Response (in JSON format with keys: 'codes' as list of {{'code', 'description', 'evidence'}}):
"""


def extract_icd10_codes(note: str) -> list:
    """Use Amazon Comprehend Medical to extract ICD-10-CM codes."""
    try:
        response = comprehend_medical.infer_icd10_cm(Text=note)
        icd10_entities = response.get('Entities', [])
        
        # Filter and structure results
        codes = []
        for entity in icd10_entities:
            # Only include entities with ICD-10-CM codes
            if 'ICD10CMConcepts' in entity and entity['ICD10CMConcepts']:
                top_concept = entity['ICD10CMConcepts'][0]  # Best match
                codes.append({
                    'code': top_concept['Code'],
                    'description': top_concept['Description'],
                    'score': top_concept['Score'],
                    'text': entity['Text']  # Source phrase from note
                })
        return codes
    except Exception as e:
        print(f"Error calling Comprehend Medical: {e}")
        return []


def generate_bedrock_response(prompt: str) -> dict:
    """Send prompt to Amazon Bedrock (using Anthropic Claude as example)."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ],
        "temperature": 0.1
    })

    try:
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v2:0")
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get('body').read())
        return json.loads(response_body['content'][0]['text'])
    except Exception as e:
        print(f"Error calling Bedrock: {e}")
        return {"error": str(e)}


def main():
    print("🔍 Step 1: Extracting ICD-10-CM codes using Amazon Comprehend Medical...\n")
    icd10_list = extract_icd10_codes(PATIENT_NOTE)

    if not icd10_list:
        print("No ICD-10-CM codes found.")
        return

    # Format for prompt
    icd10_str = "\n".join([
        f"- Code: {c['code']}, Description: {c['description']}, Evidence: '{c['text']}'"
        for c in icd10_list
    ])

    print("✅ Extracted codes:")
    print(icd10_str)
    print("\n" + "="*60 + "\n")

    # Build prompt
    prompt = PROMPT_TEMPLATE.format(
        patient_note=PATIENT_NOTE,
        icd10_codes=icd10_str
    )

    print("🧠 Step 2: Sending to Amazon Bedrock for reasoning...\n")
    result = generate_bedrock_response(prompt)

    print("📄 Final Output:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
