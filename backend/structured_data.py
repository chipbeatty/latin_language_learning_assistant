from typing import Optional
import boto3

# Model ID
MODEL_ID = "amazon.nova-micro-v1:0"
#MODEL_ID = "amazon.nova-lite-v1:0"
#MODEL_ID = "amazon.nova-pro-v1:0"

class TranscriptStructurer:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Bedrock client"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.model_id = model_id

    def structure_transcript(self, transcript: str) -> Optional[str]:
        """Structure the transcript into questions using Amazon Bedrock"""
        prompt = f"""This is a Latin language comprehension practice transcript. Ignore any introductory or ending instructions about the test.
        Focus only on extracting the actual test questions. Each question typically follows this pattern:
        1. A number (like '1.' or '2.')
        2. A setup of the situation
        3. A conversation between people
        4. A question about the conversation

        Extract each question and format them like this:

        <question>
        Introduction:
        [the situation setup in Latin]
        
        Conversation:
        [the actual dialogue in Latin]
        
        Question:
        [the question being asked in Latin]
        </question>
        ...

        Do not translate the Latin text into English.

        Here's the transcript:
        {transcript}
        """


        messages = [{
            "role": "user",
            "content": [{"text": prompt}]
        }]

        try:
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={"temperature": 0}
            )
            return response['output']['message']['content'][0]['text']
            
        except Exception as e:
            print(f"Error structuring transcript: {str(e)}")
            return None

    def save_questions(self, structured_text: str, filename: str) -> bool:
        """Save structured questions to a file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(structured_text)
            return True
        except Exception as e:
            print(f"Error saving questions: {str(e)}")
            return False

    def load_transcript(self, filename: str) -> Optional[str]:
        """Load structured questions from a file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading questions: {str(e)}")
            return None

if __name__ == "__main__":
    structurer = TranscriptStructurer()
    transcript = structurer.load_transcript("backend/transcripts/sY7L5cfCWno.txt")
    structured_text = structurer.structure_transcript(transcript)
    print(structured_text)