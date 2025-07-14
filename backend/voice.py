# ----------- ren/voice.py -----------
import sounddevice as sd
import numpy as np
import requests
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import logging
from config import config

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import speech recognition module
from speech_recognition import model as whisper_model

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

def speak(text):
    """
    Convert text to speech using ElevenLabs API and play it.
    
    Args:
        text (str): Text to convert to speech
        
    Raises:
        RuntimeError: If text-to-speech conversion or playback fails
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to speak function")
        return
    
    text = text.strip()
    print(f"Ren: {text}")
    
    # Check if voice is configured
    if not config.is_voice_enabled():
        logger.warning("Voice not configured, skipping TTS")
        return
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVEN_VOICE_ID}"
        headers = {
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
        }
        
        logger.info("Calling ElevenLabs TTS API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise RuntimeError(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        if not response.content:
            raise RuntimeError("Empty response from ElevenLabs API")
        
        # Play audio
        audio_data = BytesIO(response.content)
        audio_segment = AudioSegment.from_mp3(audio_data)
        play(audio_segment)
        
        logger.info("Speech playback completed")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during TTS: {e}")
        raise RuntimeError(f"Network error during text-to-speech: {e}")
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise RuntimeError(f"Text-to-speech failed: {e}")
