import boto3
import json
 


try:
    s3_client = boto3.client('s3', region_name='us-gov-west-1')
    textract_client = boto3.client('textract', region_name='us-gov-west-1')
except Exception as e:
    print(f"Error creating AWS clients: {e}")
    exit()

def analyze_s3_image_with_textract(bucket_name, file_key):
    """
    Analyzes an image stored in an S3 bucket using AWS Textract.

    Args:
        bucket_name (str): The name of the S3 bucket where the image is stored.
        file_key (str): The key (path) of the image file within the bucket.

    Returns:
        dict: The raw JSON response from the Textract API, or None on error.
    """
    print(f"Analyzing image 's3://{bucket_name}/{file_key}' with Textract...")
    
    try:

        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_key
                }
            }
        )
        return response
    except Exception as e:
        print(f"Error during Textract analysis: {e}")
        return None

def process_textract_response(response):
    """
    Processes the raw Textract response and prints the extracted text.

    Args:
        response (dict): The dictionary response from the Textract API.
    """
    if not response or 'Blocks' not in response:
        print("Invalid or empty response from Textract.")
        return
        
    # AIDEV-NOTE: Iterate through the blocks to find LINE and WORD blocks
    # and print their content.
    print("\n--- Extracted Text ---")
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            print(block['Text'])

if __name__ == "__main__":
    # =============================================================================
    # User-defined variables - EDIT THESE
    # =============================================================================
    # AIDEV-NOTE: Replace 'your-bucket-name' and 'your-image-file-key.jpg'
    # with your actual S3 bucket and file information.
    S3_BUCKET_NAME = 'mepcom1'
    S3_FILE_KEY = 'bitpay.png'  # e.g., 'scanned-document.png'

    # AIDEV-NOTE: The script will call the main function with your S3 details.
    textract_response = analyze_s3_image_with_textract(S3_BUCKET_NAME, S3_FILE_KEY)

    # AIDEV-NOTE: Check if the analysis was successful before processing.
    if textract_response:
        process_textract_response(textract_response)
