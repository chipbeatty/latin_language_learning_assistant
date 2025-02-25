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
        prompt = f"""This is a French language learning transcript. Create multiple choice questions from this content.
        For each piece of dialogue or vocabulary, create a question following this format:

        1. Question in French
        2. Four possible answers in French (labeled A, B, C, D)
        3. The correct answer
        4. Topic (e.g., "Vocabulary", "Grammar", "Conversation")

        Format the output as a JSON array of questions where each question has this structure:
        {{
            "question": "[French question]",
            "choices": ["A) [option]", "B) [option]", "C) [option]", "D) [option]"],
            "correct_answer": "[A, B, C, or D]",
            "topic": "[topic]"
        }}

        Here's the transcript:
        {transcript}

        Create at least 5 questions. Make sure all text (questions and answers) is in French.
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
            # Validate JSON format
            import json
            try:
                # Try to parse as JSON to validate format
                json.loads(structured_text)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON part
                import re
                json_match = re.search(r'\[\s*{.*}\s*\]', structured_text, re.DOTALL)
                if json_match:
                    structured_text = json_match.group(0)
                else:
                    print("Could not find valid JSON in response")
                    return False
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(structured_text)
            return True
        except Exception as e:
            print(f"Error saving questions: {str(e)}")
            return False

    def load_transcript(self, filename: str) -> Optional[str]:
        """Load transcript from a file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return None

if __name__ == "__main__":
    structurer = TranscriptStructurer()
    transcript = structurer.load_transcript("backend/transcripts/sY7L5cfCWno.txt")
    structured_text = structurer.structure_transcript(transcript)
    print(structured_text)