import re
from typing import Tuple

def validate_youtube_url(url: str) -> Tuple[bool, str]:
    """
    Validate YouTube URL and provide feedback
    
    Args:
        url (str): URL to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if not url:
        return False, "Please enter a URL"
        
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"
        
    # YouTube URL patterns
    youtube_patterns = [
        r'^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]{11}',
        r'^https?:\/\/(?:www\.)?youtube\.com\/v\/[\w-]{11}',
        r'^https?:\/\/youtu\.be\/[\w-]{11}'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True, "Valid YouTube URL"
            
    return False, "Invalid YouTube URL format. Please use a URL from youtube.com or youtu.be"
