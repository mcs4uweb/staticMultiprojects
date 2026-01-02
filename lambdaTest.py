import json
import boto3
from botocore.exceptions import ClientError, ParamValidationError

def lambda_handler(event, context):
    # Extract text from event input (multiple input methods supported)
    input_text = None
    
    # Method 1: Direct text in event body (API Gateway)
    if 'body' in event:
        try:
            # Handle both plain text and JSON input
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
                input_text = body.get('text')
            else:
                input_text = event['body'].get('text')
        except:
            input_text = event.get('body')
    
    # Method 2: Query string parameters
    if not input_text and 'queryStringParameters' in event:
        input_text = event['queryStringParameters'].get('text')
    
    # Method 3: Direct event property
    if not input_text:
        input_text = event.get('text')
    
    # Fallback to default text if nothing provided
    if not input_text:
        input_text = """
        aspirin is required 20 mg po daily for 2 times as tab
        """
    
    # Initialize Comprehend Medical client
    client = boto3.client('comprehendmedical', region_name='us-east-1')
    
    try:
        # Detect medical entities
        response = client.detect_entities_v2(Text=input_text)
        
        # Process and simplify the response
        simplified_entities = []
        for entity in response['Entities']:
            simplified_entities.append({
                'Text': entity['Text'],
                'Category': entity['Category'],
                'Type': entity.get('Type', 'N/A'),
                'Confidence': round(entity['Score'], 4)
            })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'original_text': input_text,
                'entities': simplified_entities,
                'full_response': response  # Remove in production if too verbose
            }, indent=2)
        }
    
    except ClientError as e:
        # Handle AWS service errors
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'AWS Service Error',
                'message': str(e)
            })
        }
    
    except ParamValidationError as e:
        # Handle input validation errors
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Validation Error',
                'message': str(e)
            })
        }
    
    except Exception as e:
        # Handle all other exceptions
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Error',
                'message': str(e)
            })
        }
