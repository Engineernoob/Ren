from ast import Bytes
from io import BytesIO
import logging
import os
import signal
import sys

from flask import Flask, jsonify, request
from flask import Response
from flask_cors import CORS

from agent import Agent
from config import config
from voice import transcribe_audio_file
from voice import listen_to_voice, speak

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize agent
try:
    ren_agent = Agent()
    logger.info("Ren agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    ren_agent = None

# Start the reminder scheduler
if ren_agent and ren_agent.scheduler:
    ren_agent.scheduler.start()
    logger.info("Reminder scheduler started")

def shutdown_handler(signum, frame):
    logger.info("Shutdown signal received, stopping scheduler...")
    if ren_agent and ren_agent.scheduler:
        ren_agent.scheduler.stop()
        logger.info("Reminder scheduler stopped")
    logger.info("Exiting application")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, shutdown_handler)  # Termination signal

# Optionally, also stop scheduler on Flask app context teardown
@app.teardown_appcontext
def teardown(exception):
    logger.info("App context teardown, stopping scheduler...")
    if ren_agent and ren_agent.scheduler:
        ren_agent.scheduler.stop()
        logger.info("Reminder scheduler stopped")

@app.route("/ask", methods=["POST"])
def handle_text():
    """Handle text-based chat requests."""
    try:
        if ren_agent is None:
            return jsonify({"error": "Agent not initialized"}), 503
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty request body"}), 400
        
        if "message" not in data:
            return jsonify({"error": "Missing 'message' in request body"}), 400
        
        user_input = data["message"]
        
        if not isinstance(user_input, str):
            return jsonify({"error": "Message must be a string"}), 400
        
        if not user_input.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"Processing text request: {user_input[:50]}...")
        response = ren_agent.process_statement(user_input)
        
        return jsonify({
            "response": response,
            "conversation_summary": ren_agent.get_conversation_summary()
        })
        
    except ValueError as e:
        logger.warning(f"Validation error in text handler: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in text handler: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/voice", methods=["POST"])
def handle_voice():
    """Handle voice-based interaction requests."""
    try:
        if ren_agent is None:
            return jsonify({"error": "Agent not initialized"}), 503
        
        if not config.is_voice_enabled():
            return jsonify({
                "error": "Voice functionality not configured. Please set ELEVENLABS_API_KEY and ELEVEN_VOICE_ID environment variables."
            }), 503
        
        logger.info("Processing voice request...")
        
        try:
            user_input = listen_to_voice()
        except RuntimeError as e:
            logger.error(f"Voice listening failed: {e}")
            return jsonify({"error": f"Voice listening failed: {str(e)}"}), 400
        
        try:
            response = ren_agent.process_statement(user_input)
        except ValueError as e:
            logger.warning(f"Invalid voice input: {e}")
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        
        try:
            speak(response)
            speech_status = "success"
        except RuntimeError as e:
            logger.error(f"Speech synthesis failed: {e}")
            speech_status = f"failed: {str(e)}"
        
        return jsonify({
            "heard": user_input,
            "response": response,
            "speech_status": speech_status,
            "conversation_summary": ren_agent.get_conversation_summary()
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in voice handler: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route("/tts", methods=["POST"])
def generate_speech():
    """Convert text to speech return MP3."""
    if ren_agent is None:
        return jsonify({"error": "Agent not initialized"}), 503
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    text = data.get("text", "")
    
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Invalid text input"}), 400
    
    try:
        audio = speak(text)
        return Response(audio, content_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route("/transcribe", methods=["POST"])
def transcribe_uploaded_audio():
    """Accepts uploaded audio and returns Whisper transcription."""
    if ren_agent is None:
        return jsonify({"error": "Agent not initialized"}), 503
    if "file" not in request.files:
        return jsonify({"error": "Missing audio file"}), 400
    
    try:
        file = request.files["file"]
        stream = BytesIO(file.read())
        text = transcribe_audio_file(stream)
        return jsonify({"text": text})
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    missing_config = config.validate_required_config()
    
    return jsonify({
        "status": "healthy",
        "agent_initialized": ren_agent is not None,
        "voice_enabled": config.is_voice_enabled(),
        "missing_config": missing_config,
        "whisper_model": config.WHISPER_MODEL
    })

@app.route("/config", methods=["GET"])
def get_config():
    """Get current configuration status."""
    missing_config = config.validate_required_config()
    
    return jsonify({
        "agent_name": config.AGENT_NAME,
        "agent_personality": config.AGENT_PERSONALITY,
        "memory_threshold": config.MEMORY_THRESHOLD,
        "whisper_model": config.WHISPER_MODEL,
        "voice_enabled": config.is_voice_enabled(),
        "missing_config": missing_config,
        "audio_settings": {
            "sample_rate": config.AUDIO_SAMPLE_RATE,
            "duration": config.AUDIO_DURATION
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    missing_config = config.validate_required_config()
    if missing_config:
        logger.warning(f"Missing configuration: {missing_config}")
        logger.warning("Voice functionality will be disabled")
    
    logger.info("Starting Ren voice assistant backend...")
    app.run(debug=True, host='0.0.0.0', port=5001)