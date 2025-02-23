import boto3
import json
from typing import Dict, Any, Optional

MODEL_ID = "anthropic.claude-v2"

class BedrockChat:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Bedrock chat client"""
        try:
            # Initialize the Bedrock client using AWS credentials from environment
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name="us-east-1"
            )
            self.model_id = model_id
        except Exception as e:
            print("""Error: Could not initialize Amazon Bedrock client.
                  Please ensure you have:
                  1. Valid AWS credentials in your environment variables
                  2. Appropriate permissions to access Bedrock
                  3. Bedrock is available in your region""")
            raise e

    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate a response using the Bedrock API
        
        Args:
            message (str): Input message
            inference_config (Optional[Dict[str, Any]]): Optional inference configuration
            
        Returns:
            Optional[str]: Generated response if successful, None otherwise
        """
        try:
            # Prepare the request body
            body = {
                "prompt": f"\n\nHuman: {message}\n\nAssistant:",
                "max_tokens_to_sample": 500,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            # Update with any custom inference config
            if inference_config:
                body.update(inference_config)
            
            # Invoke the model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Parse and return the response
            response_body = json.loads(response.get('body').read())
            return response_body.get('completion')
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None
