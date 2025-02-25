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
            Optional[str]: Generated response or None if there was an error
        """
        if inference_config is None:
            inference_config = {
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 1,
                "top_k": 250
            }

        try:
            # Format the prompt for Claude
            prompt = f"Human: {message}\n\nAssistant:"
            
            # Create the request body
            body = json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": inference_config["max_tokens"],
                "temperature": inference_config["temperature"],
                "top_p": inference_config["top_p"],
                "top_k": inference_config["top_k"]
            })

            # Make the API call
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )

            # Parse the response
            response_body = json.loads(response['body'].read())
            return response_body.get('completion')
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None
