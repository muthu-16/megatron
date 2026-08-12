import logging
import webbrowser
import urllib.parse
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class YouTubeController:
    """Controls YouTube search, playback, and transcript extraction."""

    def __init__(self):
        pass

    def search(self, query: str) -> bool:
        """
        Search YouTube for a specific query by opening the browser.
        """
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(url)
            logger.info(f"Opened YouTube search for: {query}")
            return True
        except Exception as e:
            logger.error(f"Error searching YouTube for '{query}': {e}")
            return False

    def play(self, video_id_or_url: str) -> bool:
        """
        Play a YouTube video by opening its URL.
        """
        try:
            if "youtube.com" in video_id_or_url or "youtu.be" in video_id_or_url:
                url = video_id_or_url
            else:
                url = f"https://www.youtube.com/watch?v={video_id_or_url}"
                
            webbrowser.open(url)
            logger.info(f"Playing YouTube video: {url}")
            return True
        except Exception as e:
            logger.error(f"Error playing YouTube video '{video_id_or_url}': {e}")
            return False

    def get_transcript(self, video_id: str, languages: List[str] = ['en']) -> Optional[List[Dict[str, Any]]]:
        """
        Get the transcript of a YouTube video using youtube_transcript_api.
        
        Args:
            video_id: The YouTube video ID.
            languages: List of language codes to try.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Extract video ID if a full URL is provided
            if "v=" in video_id:
                video_id = video_id.split("v=")[1][:11]
            elif "youtu.be/" in video_id:
                video_id = video_id.split("youtu.be/")[1][:11]
                
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            logger.info(f"Successfully retrieved transcript for video: {video_id}")
            return transcript
        except ImportError:
            logger.error("youtube_transcript_api is not installed. Cannot get transcript.")
            return None
        except Exception as e:
            logger.error(f"Error getting transcript for video '{video_id}': {e}")
            return None

    def format_results(self, transcript: List[Dict[str, Any]]) -> str:
        """
        Format a raw transcript into a readable text block.
        """
        if not transcript:
            return ""
            
        try:
            formatted_text = []
            for item in transcript:
                text = item.get('text', '').replace('\n', ' ')
                formatted_text.append(text)
                
            return " ".join(formatted_text)
        except Exception as e:
            logger.error(f"Error formatting transcript: {e}")
            return ""
