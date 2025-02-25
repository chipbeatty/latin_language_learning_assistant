from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict, Tuple
from .utils import validate_youtube_url


class YouTubeTranscriptDownloader:
    def __init__(self, languages: List[str] = ["fr", "en"]):
        self.languages = languages

    def extract_video_id(self, url: str) -> Tuple[Optional[str], str]:
        """
        Extract video ID from YouTube URL with validation
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Tuple[Optional[str], str]: (video_id if found, error message if any)
        """
        # First validate the URL format
        is_valid, message = validate_youtube_url(url)
        if not is_valid:
            return None, message
            
        # Extract ID from valid URL
        if "v=" in url:
            video_id = url.split("v=")[1][:11]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1][:11]
        else:
            return None, "Could not extract video ID from URL"
            
        return video_id, ""

    def get_transcript(self, url_or_id: str) -> Optional[List[Dict]]:
        """
        Download YouTube Transcript
        
        Args:
            url_or_id (str): YouTube video ID or URL
            
        Returns:
            Optional[List[Dict]]: Transcript if successful, None otherwise
        """
        # Extract video ID if full URL is provided
        if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
            video_id, error = self.extract_video_id(url_or_id)
            if not video_id:
                print(f"Error: {error}")
                return None
        else:
            # Assume it's already a video ID
            video_id = url_or_id

        print(f"Downloading transcript for video ID: {video_id}")
        
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=self.languages)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def save_transcript(self, transcript: List[Dict], filename: str) -> bool:
        """
        Save transcript to file
        
        Args:
            transcript (List[Dict]): Transcript data
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Save to the transcripts directory in the backend folder
        filename = f"backend/transcripts/{filename}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
            return True
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return False

def main(video_url, print_transcript=False):
    # Initialize downloader
    downloader = YouTubeTranscriptDownloader()
    
    # Get transcript
    transcript = downloader.get_transcript(video_url)
    
    if transcript:
        # Save transcript
        video_id = downloader.extract_video_id(video_url)
        if downloader.save_transcript(transcript, video_id):
            print(f"Transcript saved successfully to {video_id}.txt")
            #Print transcript if True
            if print_transcript:
                # Print transcript
                for entry in transcript:
                    print(f"{entry['text']}")
        else:
            print("Failed to save transcript")
        
    else:
        print("Failed to get transcript")

if __name__ == "__main__":
    video_id = "https://www.youtube.com/watch?v=aWUlrL6E_QU&list=PLjqqMkeHFt1E_lRi9nQvtmP9Od2JokI1J"  # Extract from URL: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    transcript = main(video_id, print_transcript=True)
        