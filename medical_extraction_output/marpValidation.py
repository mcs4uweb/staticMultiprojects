import boto3
import json
import os

# Initialize AWS clients
COMPREHEND_REGION = os.getenv('COMPREHEND_REGION', os.getenv('AWS_REGION', 'us-gov-west-1'))
BEDROCK_REGION = os.getenv('BEDROCK_REGION', os.getenv('AWS_REGION', 'us-gov-west-1'))

comprehend_medical = boto3.client('comprehendmedical', region_name=COMPREHEND_REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
# Control-plane client to list supported models in region
bedrock_control = boto3.client('bedrock', region_name=BEDROCK_REGION)

# ?? MARP-AUTHORIZED ICD-10 CODES (from your SMPG)
# These are the ONLY codes allowed for MARP eligibility.
# In practice, load this from a secure config file or database.
MARP_AUTHORIZED_CODES = {
    "F90.0",   # ADHD, predominantly inattentive type
    "F90.1",   # ADHD, predominantly hyperactive-impulsive type
    "F90.2",   # ADHD, combined type
    "R10.9",   # Unspecified abdominal pain (example from prior note)
    # Add other SMPG-specified codes here
}

PATIENT_NOTE = """The patient is a 71-year-old female patient of Dr. X. The patient presented to the 
emergency room last evening with approximately 7-day to 8-day history of abdominal pain, which has 
been persistent. She has had no definite fevers or chills and no history of jaundice. The patient denies 
any significant recent weight loss."""

PROMPT_TEMPLATE = """
You are a clinical coding assistant supporting MARP (Medical Affirmative Review Process) evaluations.
Only include ICD-10-CM codes that are BOTH:
  (a) extracted from the patient note, AND
  (b) explicitly authorized under MARP policy.

For each included code:
1. Provide the full description.
2. Cite the exact phrase(s) from the note that support it.
3. Confirm it is a MARP-authorized code.

Patient Note:
{patient_note}

MARP-Authorized ICD-10-CM Codes Extracted:
{marp_codes}

Response (JSON format with key 'marp_eligible_codes' as list of {{'code', 'description', 'evidence'}}):
"""


def extract_icd10_codes(note: str) -> list:
    """Extract ICD-10-CM codes using Amazon Comprehend Medical."""
    try:
        response = comprehend_medical.infer_icd10_cm(Text=note)
        entities = response.get('Entities', [])
        codes = []
        for entity in entities:
            concepts = entity.get('ICD10CMConcepts', [])
            if concepts:
                top = concepts[0]
                codes.append({
                    'code': top['Code'],
                    'description': top['Description'],
                    'score': top['Score'],
                    'text': entity['Text']
                })
        return codes
    except Exception as e:
        print(f"?? Comprehend Medical error: {e}")
        return []


def filter_marp_eligible_codes(icd10_list: list) -> list:
    """Filter to ONLY codes that are MARP-authorized."""
    marp_eligible = []
    for code_obj in icd10_list:
        if code_obj['code'] in MARP_AUTHORIZED_CODES:
            marp_eligible.append(code_obj)
    return marp_eligible


def generate_bedrock_response(prompt: str) -> dict:
    """Send to Amazon Bedrock and parse JSON response."""
    try:
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

        # Preflight: ensure modelId exists in this region
        try:
            summaries = bedrock_control.list_foundation_models().get('modelSummaries', [])
            available_ids = {m.get('modelId') for m in summaries if 'modelId' in m}
            if model_id not in available_ids:
                print("?? Bedrock validation: Model ID not found in region.")
                print(f"   - Requested model: {model_id}")
                print(f"   - BEDROCK_REGION: {BEDROCK_REGION}")
                # Offer Anthropic suggestions if any
                anthro = [m for m in available_ids if isinstance(m, str) and m.startswith('anthropic.')]
                if anthro:
                    print("   - Available Anthropic models in region:")
                    for mid in anthro[:6]:
                        print(f"     * {mid}")
                    print("   - Set BEDROCK_MODEL_ID to one of the above.")
                else:
                    print("   - No Anthropic models found in this region. Choose a region with Anthropic availability (e.g., us-east-1) or update code to use a supported provider.")
                return {"error": f"Model '{model_id}' not available in {BEDROCK_REGION}"}
        except Exception as _e:
            # Non-fatal: proceed; invoke will still surface any invalid id error
            pass

        # Build provider-specific payloads and parsing
        if model_id.startswith("anthropic."):
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ],
                "temperature": 0.0
            })
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            response_text = json.loads(response['body'].read())['content'][0]['text']
            return json.loads(response_text)
        elif model_id.startswith("amazon.titan-text"):
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.0
                }
            })
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            rb = json.loads(response['body'].read())
            output_text = rb.get('results', [{}])[0].get('outputText', '')
            return json.loads(output_text) if output_text else {"error": "Empty Titan response."}
        else:
            # Fallback to Anthropic-style payload
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ],
                "temperature": 0.0
            })
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            response_text = json.loads(response['body'].read())['content'][0]['text']
            return json.loads(response_text)
    except Exception as e:
        msg = str(e)
        if (
            "identtifier is invalid" in msg
            or "identifier is invalid" in msg
            or "model identifier is invalid" in msg
            or "Model not found" in msg
        ):
            print("?? Bedrock hint: Ensure the chosen model is available in your BEDROCK_REGION and that you have access to it.")
            print(f"   - BEDROCK_REGION: {BEDROCK_REGION}")
            print("   - Try a supported region like 'us-east-1' or 'us-west-2'.")
            print("   - Or set BEDROCK_MODEL_ID to a model that exists in your region.")
        print(f"?? Bedrock error: {e}")
        return {"error": str(e)}


def main():
    print("?? Step 1: Extracting ICD-10-CM codes...")
    all_codes = extract_icd10_codes(PATIENT_NOTE)

    print("\n?? All extracted codes:")
    for c in all_codes:
        status = "? MARP-AUTHORIZED" if c['code'] in MARP_AUTHORIZED_CODES else "? NOT MARP-AUTHORIZED"
        print(f"  {c['code']} ({c['description']}) - {status}")

    print("\n??? Step 2: Applying MARP rule validation...")
    marp_codes = filter_marp_eligible_codes(all_codes)

    if not marp_codes:
        print("?? No MARP-authorized codes found. Condition not eligible under MARP.")
        return

    # Format for prompt
    marp_str = "\n".join([
        f"- Code: {c['code']}, Description: {c['description']}, Evidence: '{c['text']}'"
        for c in marp_codes
    ])

    print("\n? MARP-eligible codes:")
    print(marp_str)
    print("\n" + "="*60 + "\n")

    prompt = PROMPT_TEMPLATE.format(
        patient_note=PATIENT_NOTE,
        marp_codes=marp_str
    )

    print("?? Step 3: Generating MARP-compliant summary via Bedrock...\n")
    result = generate_bedrock_response(prompt)

    print("?? Final MARP Output:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
