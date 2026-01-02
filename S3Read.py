import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError
import time

class DocumentProcessor:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name='us-east-1'):
        """
        Initialize AWS clients for S3 and Textract
        
        Args:
            aws_access_key_id: AWS access key (optional if using IAM roles or environment variables)
            aws_secret_access_key: AWS secret key (optional if using IAM roles or environment variables)
            region_name: AWS region (default: us-east-1)
        """
        try:
            # Initialize AWS clients
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
            
            self.s3_client = session.client('s3')
            self.textract_client = session.client('textract')
            self.region_name = region_name
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found. Please configure your credentials.")
    
    def upload_file_to_s3(self, file_path, bucket_name, object_key):
        """
        Upload a file to S3 bucket
        
        Args:
            file_path: Local path to the file
            bucket_name: S3 bucket name
            object_key: S3 object key (file name in bucket)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.upload_file(file_path, bucket_name, object_key)
            print(f"File uploaded successfully to s3://{bucket_name}/{object_key}")
            return True
        except FileNotFoundError:
            print(f"Error: File {file_path} not found")
            return False
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
    
    def analyze_document_sync(self, bucket_name, object_key):
        """
        Synchronously analyze a document using Textract (for single-page documents)
        
        Args:
            bucket_name: S3 bucket name
            object_key: S3 object key
            
        Returns:
            dict: Textract response or None if error
        """
        try:
            response = self.textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': object_key
                    }
                }
            )
            return response
        except ClientError as e:
            print(f"Error analyzing document: {e}")
            return None
    
    def analyze_document_async(self, bucket_name, object_key):
        """
        Asynchronously analyze a document using Textract (for multi-page documents)
        
        Args:
            bucket_name: S3 bucket name
            object_key: S3 object key
            
        Returns:
            dict: Final Textract response or None if error
        """
        try:
            # Start document analysis job
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': object_key
                    }
                }
            )
            
            job_id = response['JobId']
            print(f"Started async job with ID: {job_id}")
            
            # Poll for completion
            while True:
                response = self.textract_client.get_document_text_detection(JobId=job_id)
                status = response['JobStatus']
                
                if status == 'SUCCEEDED':
                    print("Document analysis completed successfully")
                    return response
                elif status == 'FAILED':
                    print("Document analysis failed")
                    return None
                else:
                    print(f"Job status: {status}. Waiting...")
                    time.sleep(5)
                    
        except ClientError as e:
            print(f"Error in async document analysis: {e}")
            return None
    
    def extract_text_from_response(self, textract_response):
        """
        Extract text from Textract response
        
        Args:
            textract_response: Response from Textract API
            
        Returns:
            str: Extracted text
        """
        if not textract_response:
            return ""
        
        text_blocks = []
        
        # Extract text blocks
        for block in textract_response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_blocks.append(block['Text'])
        
        return '\n'.join(text_blocks)
    
    def extract_structured_data(self, textract_response):
        """
        Extract structured data from Textract response
        
        Args:
            textract_response: Response from Textract API
            
        Returns:
            dict: Structured data including words, lines, and pages
        """
        if not textract_response:
            return {}
        
        result = {
            'pages': [],
            'lines': [],
            'words': []
        }
        
        for block in textract_response.get('Blocks', []):
            if block['BlockType'] == 'PAGE':
                result['pages'].append({
                    'id': block['Id'],
                    'geometry': block['Geometry'],
                    'confidence': block.get('Confidence', 0)
                })
            elif block['BlockType'] == 'LINE':
                result['lines'].append({
                    'id': block['Id'],
                    'text': block['Text'],
                    'confidence': block.get('Confidence', 0),
                    'geometry': block['Geometry']
                })
            elif block['BlockType'] == 'WORD':
                result['words'].append({
                    'id': block['Id'],
                    'text': block['Text'],
                    'confidence': block.get('Confidence', 0),
                    'geometry': block['Geometry']
                })
        
        return result

# Example usage
def main():
    # Initialize the document processor
    processor = DocumentProcessor(region_name='us-east-1')
    
    # Configuration
    bucket_name = 'your-bucket-name'
    local_file_path = '/path/to/your/document.pdf'  # or .jpg, .png, .tiff
    s3_object_key = 'documents/sample-document.pdf'
    
    # Step 1: Upload file to S3 (optional if file is already in S3)
    print("Uploading file to S3...")
    upload_success = processor.upload_file_to_s3(local_file_path, bucket_name, s3_object_key)
    
    if not upload_success:
        return
    
    # Step 2: Analyze document with Textract
    print("Analyzing document with Textract...")
    
    # For single-page documents, use synchronous analysis
    textract_response = processor.analyze_document_sync(bucket_name, s3_object_key)
    
    # For multi-page documents, use asynchronous analysis
    # textract_response = processor.analyze_document_async(bucket_name, s3_object_key)
    
    if not textract_response:
        print("Failed to analyze document")
        return
    
    # Step 3: Extract text
    print("Extracting text...")
    extracted_text = processor.extract_text_from_response(textract_response)
    
    print("Extracted Text:")
    print("=" * 50)
    print(extracted_text)
    
    # Step 4: Get structured data (optional)
    print("\nExtracting structured data...")
    structured_data = processor.extract_structured_data(textract_response)
    
    print(f"Pages found: {len(structured_data['pages'])}")
    print(f"Lines found: {len(structured_data['lines'])}")
    print(f"Words found: {len(structured_data['words'])}")
    
    # Step 5: Save results (optional)
    with open('extracted_text.txt', 'w', encoding='utf-8') as f:
        f.write(extracted_text)
    
    with open('structured_data.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, default=str)
    
    print("Results saved to extracted_text.txt and structured_data.json")

if __name__ == "__main__":
    main()