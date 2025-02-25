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
                text="<prosody rate='slow'>Écoutez la question et choisissez la meilleure réponse.</prosody><break time='1s'/>",
                voice_id=self.male_voice,
                role='intro'
            ),
            # Question
            AudioSegment(
                text=f"<prosody rate='slow'>{question_data['question']}</prosody><break time='1s'/>",
                voice_id=question_voice,
                role='question'
            )
        ]
        
        # Add answer choices
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # 65 is ASCII for 'A'
            segments.append(AudioSegment(
                text=f"Option {letter}<break time='0.7s'/>{choice}<break time='1s'/>",
                voice_id=answer_voice,
                role=f'answer_{letter}'
            ))
        
        return segments


    def _generate_audio_segment(self, segment: AudioSegment) -> Optional[str]:
        """Generate audio for a single segment using Amazon Polly"""
        try:
            print(f"Generating audio for text: '{segment.text}' using voice: {segment.voice_id}")
            response = self.polly_client.synthesize_speech(
                Engine='neural',
                LanguageCode='fr-FR',
                OutputFormat='mp3',
                TextType='ssml',
                Text=f'<speak>{segment.text}</speak>',
                VoiceId=segment.voice_id
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                if "AudioStream" in response:
                    temp_file.write(response["AudioStream"].read())
                    print(f"Successfully saved audio to {temp_file.name}")
                    return temp_file.name
                else:
                    print("No AudioStream in response")
            return None
        except Exception as e:
            import traceback
            print(f"Error generating audio segment: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return None

    def generate_audio(self, question_data: Dict, question_voice_is_male: bool = False) -> tuple[Optional[str], Optional[str]]:
        """Generate full audio file for a question
        Returns:
            Tuple of (audio_path, error_message)
        """
        try:
            print(f"Received question data: {question_data}")
            # Generate conversation script with voice alternation
            segments = self._generate_conversation_script(question_data, question_voice_is_male)
            if not segments:
                return None, "No segments were generated from the conversation script"
            
            print("Starting audio generation for segments...")
            # Generate audio for each segment
            audio_files = []
            for i, segment in enumerate(segments):
                print(f"Processing segment {i+1}/{len(segments)}")
                audio_file = self._generate_audio_segment(segment)
                if audio_file:
                    audio_files.append(audio_file)
                else:
                    print(f"Failed to generate audio for segment {i+1}")
            
            if not audio_files:
                print("No audio files were generated from any segment")
                return None, "No audio files were generated"
            
            # Create output filename based on question
            output_filename = f"question_{hash(question_data['question'])}.mp3"
            output_path = self.output_dir / output_filename
            
            # Combine audio files using ffmpeg
            concat_file = "concat.txt"
            with open(concat_file, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
            
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', concat_file, '-c', 'copy', str(output_path)
            ], check=True)
            
            # Cleanup temporary files
            os.remove(concat_file)
            for file in audio_files:
                os.remove(file)
            
            return str(output_path), None
        except Exception as e:
            import traceback
            print(f"Error generating audio: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return None, f"Error generating audio: {str(e)}"
