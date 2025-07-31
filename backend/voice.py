# ----------- ren/voice.py -----------
from io import BytesIO
import logging
import os
import tempfile

from click import style
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import requests
import sounddevice as sd

from config import config
from speech_recognition import model as whisper_model

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TONE_TO_STYLE = {
    "warm": "narration",
    "calm": "conversational",
    "serious": "serious",
    "tense": "empathetic",
    "low": "sad",
    "light": "cheerful",
    "sharp": "assertive"
}


# Global whisper model instance (lazy loading)
_whisper_model = None

def get_whisper_model():
    """Get or initialize the Whisper model (lazy loading)."""
    global _whisper_model
    if _whisper_model is None:
        try:
            logger.info(f"Loading Whisper model: {config.WHISPER_MODEL}")
            _whisper_model = whisper_model
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Could not initialize Whisper model: {e}")
    return _whisper_model

def listen_to_voice():
    """
    Record audio from microphone and transcribe using Whisper.
    
    Returns:
        str: Transcribed text from audio
        
    Raises:
        RuntimeError: If audio recording or transcription fails
    """
    try:
        fs = config.AUDIO_SAMPLE_RATE
        seconds = config.AUDIO_DURATION
        
        logger.info("🎙️ Listening...")
        print("🎙️ Listening...")
        
        # Record audio
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype=np.float32)
        sd.wait()
        
        if recording is None or len(recording) == 0:
            raise RuntimeError("Failed to record audio")
        
        # Process audio
        audio = np.squeeze(recording)
        
        # Transcribe using Whisper
        model = get_whisper_model()
        result = model.transcribe(audio)
        
        if not result or 'text' not in result:
            raise RuntimeError("Failed to transcribe audio")

        # Ensure result["text"] is a string before calling strip()
        if not isinstance(result["text"], str):
            raise RuntimeError("Transcription result is not a valid string")

        transcribed_text = result["text"].strip()
        logger.info(f"📝 Transcribed: {transcribed_text}")
        print(f"📝 You said: {transcribed_text}")

        if not transcribed_text:
            raise RuntimeError("No speech detected")
        
        return transcribed_text
        
    except Exception as e:
        logger.error(f"Voice listening failed: {e}")
        raise RuntimeError(f"Voice listening failed: {e}")
    
def transcribe_audio_file(file_stream: BytesIO) -> str:
    """
    Transcribe uploaded audio using Whisper (requires writing to temp file).

    Args:
        file_stream (BytesIO): Incoming audio stream

    Returns:
        str: Transcribed text
    """
    try:
        model = get_whisper_model()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(file_stream.read())
            tmp_path = tmp.name

        result = model.transcribe(tmp_path)
        os.remove(tmp_path)  # Clean up the temp file

        if not result or 'text' not in result:
            raise RuntimeError("Transcription failed or no text returned")

        text = result.get("text", "")
        if isinstance(text, list):
            text = "".join(str(t) for t in text)
        elif not isinstance(text, str):
            raise RuntimeError("Transcription text is not a valid string or list")

        return text.strip()
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise RuntimeError(f"Transcription failed: {e}")


def speak(text: str, tone: str = "calm") -> bytes:
    """
    Convert text to speech using ElevenLabs API and return MP3 bytes.

    Args:
        text (str): Text to convert to speech

    Returns:
        bytes: MP3 audio content

    Raises:
        RuntimeError: On API or conversion error
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to speak function")
        return b""

    text = text.strip()
    logger.info(f"Ren: {text}")

    if not config.is_voice_enabled():
        logger.warning("Voice not configured, skipping TTS")
        return b""

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVEN_VOICE_ID}"
        headers = {
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        
        style = TONE_TO_STYLE.get(tone, "conversational")
        
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.75, "style": style}
        }

        logger.info("Calling ElevenLabs TTS API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"ElevenLabs API error: {response.status_code} - {response.text}")

        return response.content

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during TTS: {e}")
        raise RuntimeError(f"Network error during text-to-speech: {e}")
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise RuntimeError(f"Text-to-speech failed: {e}")