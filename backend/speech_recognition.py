# speech_recognition.py
import queue
import threading

import numpy as np
import sounddevice as sd
import torch
import whisper

# Load Whisper model
model = whisper.load_model("base")

SAMPLE_RATE = 16000
BLOCK_SIZE = int(SAMPLE_RATE * 0.5)  # 0.5 seconds

audio_queue = queue.Queue()
stop_flag = threading.Event()

def audio_callback(indata, frames, time, status):
    if status:
        print("[AudioStream Warning]", status)
    audio_queue.put(indata.copy())

def stream_transcription(callback):
    """
    Continuously transcribe live audio and call `callback(text)` with partial results.
    Supports both Whisper and faster-whisper decoding styles.
    """
    print("[Ren] Starting real-time transcription...")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=BLOCK_SIZE, callback=audio_callback):
        audio_buffer = []

        while not stop_flag.is_set():
            try:
                chunk = audio_queue.get(timeout=1)
                audio_np = np.squeeze(chunk)
                audio_buffer.extend(audio_np)

                if len(audio_buffer) >= SAMPLE_RATE * 3:
                    audio_input = np.array(audio_buffer[-SAMPLE_RATE * 5:])
                    mel = whisper.log_mel_spectrogram(audio_input).to(model.device)

                    with torch.no_grad():
                        options = whisper.DecodingOptions(language="en", fp16=False, without_timestamps=True)
                        result = whisper.decode(model, mel, options)

                    # Unified decoding handling
                    if isinstance(result, list):  # For faster-whisper-style
                        text = " ".join([r.text.strip() for r in result if hasattr(r, "text")])
                    else:  # Standard OpenAI Whisper
                        text = result.text.strip() if hasattr(result, "text") else ""

                    if text:
                        print("[Whisper Partial]", text)
                        callback(text)

                    audio_buffer = []
            except queue.Empty:
                continue

def stop_stream():
    stop_flag.set()
    print("[Ren] Stopping transcription.")