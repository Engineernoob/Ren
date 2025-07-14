# speech_recognition.py
# Real-time speech recognition using Whisper
import whisper as whisper_lib

# Whisper model instance
model = whisper_lib.load_model("base")

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes audio file using Whisper.
    :param audio_path: Path to the target audio file.
    :return: Transcribed text.
    """
    result = model.transcribe(audio_path)
    text = result['text']
    # Ensure the return value is always a string
    if isinstance(text, list):
        text = ' '.join(text)
    return text
