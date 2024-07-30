import asyncio
import assemblyai as aai
from src.autobots.core.settings import Settings, SettingsProvider
from functools import lru_cache
from pydantic import BaseModel
from typing import Optional


class TranscriptionReq(BaseModel):
    file_url: str | None = None

class AssemblyAIClient:
    def __init__(self, api_key: str):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()

    async def transcribe(self, audio_url: str) -> Optional[str]:
        """
        Asynchronously transcribe audio from a given URL using AssemblyAI.
        
        :param audio_url: URL of the audio file to transcribe
        :return: Transcribed text or None if transcription failed
        """
        config = aai.TranscriptionConfig(speaker_labels=True, sentiment_analysis=True)
        transcript = await asyncio.to_thread(self.transcriber.transcribe, audio_url, config)
        if not transcript or not transcript.utterances:
            return None
        texts = [f"Speaker {utterance.speaker}: {utterance.text}" for utterance in transcript.utterances]
        sentitments = [f"{sentiment_result.text} {sentiment_result.sentiment} Timestamp: {sentiment_result.start} - {sentiment_result.end}" for sentiment_result in transcript.sentiment_analysis]

        return ''.join(texts)+ ''.join(sentitments)

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