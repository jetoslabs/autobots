from src.autobots.core.settings import Settings, SettingsProvider
import requests
import time
from typing import Optional
from functools import lru_cache
from pydantic import BaseModel, HttpUrl

class TranscriptionReq(BaseModel):
    file_url: HttpUrl | None = None
    
class AssemblyAIClient:
    BASE_URL = "https://api.assemblyai.com/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }

    def transcribe(self, audio_url: str) -> Optional[str]:
        """
        Transcribe audio from a given URL using AssemblyAI.
        
        :param audio_url: URL of the audio file to transcribe
        :return: Transcribed text or None if transcription failed
        """
        # Create transcription request
        response = requests.post(
            f"{self.BASE_URL}/transcript",
            json={"audio_url": audio_url},
            headers=self.headers
        )
        response.raise_for_status()
        transcript_id = response.json()["id"]

        # Poll for transcription result
        while True:
            status, text = self._get_transcription_status(transcript_id)
            
            if status == "completed":
                return text
            elif status == "error":
                return None
            
            # Wait before polling again
            time.sleep(5)

    def _get_transcription_status(self, transcript_id: str) -> tuple[str, Optional[str]]:
        """
        Get the status of a transcription job.
        
        :param transcript_id: ID of the transcription job
        :return: Tuple of (status, transcribed_text)
        """
        response = requests.get(
            f"{self.BASE_URL}/transcript/{transcript_id}",
            headers=self.headers
        )
        response.raise_for_status()
        result = response.json()
        
        return result["status"], result.get("text")
@lru_cache
def get_assemblyai(settings: Settings = SettingsProvider.sget()) -> AssemblyAIClient:
    """
    Create and return an instance of AssemblyAIClient using the API key from the settings provider.
    
    :param settings: An instance of SettingsProvider
    :return: An instance of AssemblyAIClient
    :raises ValueError: If the ASSEMBLYAI_API_KEY setting is not found
    """
    api_key = settings.ASSEMBLYAI_API_KEY
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY setting is not found")
    
    return AssemblyAIClient(api_key)