import boto3
import json
import os
import tempfile
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AudioSegment:
    text: str
    voice_id: str
    role: str  # 'announcer', 'speaker1', 'speaker2', etc.

class AudioGenerator:
    def __init__(self):
        """Initialize Polly and Bedrock clients"""
        # Create a session with the profile
        session = boto3.Session(profile_name='primary')
        
        # Use the session to create clients
        self.polly_client = session.client('polly', region_name='us-east-1')
        self.bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        # Define French voices - using only neural voices
        self.male_voice = 'Remi'
        self.female_voice = 'Gabrielle'
        
        # Create output directory if it doesn't exist
        self.output_dir = Path("frontend/static/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_conversation_script(self, question_data: Dict, question_voice_is_male: bool) -> List[AudioSegment]:
        """Generate audio script with alternating voices"""
        # Get choices from the question data
        choices = question_data.get('choices', [])
        
        # Determine voices for this question
        question_voice = self.male_voice if question_voice_is_male else self.female_voice
        answer_voice = self.female_voice if question_voice_is_male else self.male_voice
        
        # Create the segments
        segments = [
            # Introduction (always male voice)
            AudioSegment(
                text="<speak>Écoutez la question et choisissez la meilleure réponse.<break time='1s'/></speak>",
                voice_id=self.male_voice,
                role='intro'
            ),
            # Question
            AudioSegment(
                text=f"<speak>{question_data['question']}<break time='1s'/></speak>",
                voice_id=question_voice,
                role='question'
            )
        ]
        
        # Add context if available
        if 'context' in question_data:
            segments.insert(1, AudioSegment(
                text=f"<speak>{question_data['context']}<break time='1s'/></speak>",
                voice_id=answer_voice,
                role='context'
            ))
        
        # Add choices if available
        if choices:
            for i, choice in enumerate(choices):
                segments.append(AudioSegment(
                    text=f"<speak>{choice}<break time='0.5s'/></speak>",
                    voice_id=answer_voice,
                    role=f'choice_{i+1}'
                ))
        
        return segments

    def generate_audio(self, question_data: Dict, question_voice_is_male: bool = True) -> str:
        """Generate audio for a question and return the path to the audio file"""
        # Create a unique filename based on the question content
        filename = f"question_{hash(json.dumps(question_data))}.mp3"
        output_path = self.output_dir / filename
        
        # If file already exists, return its path
        if output_path.exists():
            return str(output_path)
        
        # Generate the conversation script
        segments = self._generate_conversation_script(question_data, question_voice_is_male)
        
        # Generate audio for each segment
        temp_files = []
        try:
            for i, segment in enumerate(segments):
                # Generate audio with Polly
                response = self.polly_client.synthesize_speech(
                    Engine='neural',
                    LanguageCode='fr-FR',
                    OutputFormat='mp3',
                    Text=segment.text,
                    TextType='ssml',
                    VoiceId=segment.voice_id
                )
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_files.append(temp_file.name)
                    if 'AudioStream' in response:
                        temp_file.write(response['AudioStream'].read())
            
            # Concatenate all audio files
            concat_command = ['ffmpeg', '-y']
            for temp_file in temp_files:
                concat_command.extend(['-i', temp_file])
            concat_command.extend(['-filter_complex', f'concat=n={len(temp_files)}:v=0:a=1', str(output_path)])
            
            subprocess.run(concat_command, check=True)
            return str(output_path)
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
