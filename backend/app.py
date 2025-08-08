from ast import Bytes
from io import BytesIO
import logging
import os
import signal
import sys

from flask import Flask, jsonify, request
from flask import Response
from flask_cors import CORS
from torch.utils import data

from agent import Agent
from backend.checkin_flow import CheckInState, handle_checkin_input
from backend.intent_router import route_intent
from config import config
from voice import transcribe_audio_file
from voice import listen_to_voice, speak

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

checkin_state: CheckInState = CheckInState()

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

@app.route("/chat", methods=["POST"])
def handle_text():
    try:
        if ren_agent is None:
            return jsonify({"error": "Agent not initialized"}), 503

        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json() or {}
        user_input = data.get("message", "")
        if not isinstance(user_input, str) or not user_input.strip():
            return jsonify({"error": "Message must be a non-empty string"}), 400

        # ── Intent routing ───────────────────────────────
        intent = route_intent(user_input)
        logger.info(f"Intent: {intent.name} (conf={intent.confidence:.2f}) slots={intent.slots}")

        # graceful exit/farewell
        if intent.name in ("exit", "farewell"):
            return jsonify({"response": "👋 Understood. I’ll be here when you need me."}), 200

        # structured check-in flow
        if intent.name == "checkin":
            global checkin_state
            # If inactive, kick it off; else advance with input
            if not checkin_state.active:
                checkin_state = CheckInState(active=True, phase="intro")
                reply = "Let’s do a quick check-in. How are you feeling right now?"
                return jsonify({"response": reply, "phase": checkin_state.phase, "checkin": True}), 200
            new_state, reply, done = handle_checkin_input(checkin_state, user_input)
            checkin_state = new_state
            if done:
                # optional: persist summary in agent memory
                try:
                    ren_agent.memory_store.set("last_checkin_summary", checkin_state.summary or "")
                except Exception:
                    pass
                checkin_state = CheckInState()  # reset
            return jsonify({
                "response": reply,
                "phase": checkin_state.phase,
                "done": done,
                "checkin": True
            }), 200

        # simple reminder stub (hook to your scheduler)
        if intent.name == "reminder":
            task = intent.slots.get("task", "").strip() or "that thing you mentioned"
            when = intent.slots.get("when", "").strip()
            # TODO: integrate with ren_agent.scheduler if you have a method for this
            # ren_agent.create_reminder(task, when)
            text = f"Reminder noted: “{task}”{f' at {when}' if when else ''}. I’ll handle scheduling next."
            return jsonify({"response": text, "intent": "reminder"}), 200

        # weather/smalltalk/agent_action could be custom; for now, let LLM handle
        # or branch here with your own handlers
        # ────────────────────────────────────────────────

        # default: send to your LLM agent
        response = ren_agent.process_statement(user_input)
        return jsonify({
            "response": response,
            "conversation_summary": ren_agent.get_conversation_summary(),
            "intent": intent.name
        }), 200

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
            last_sentiment = ren_agent.memory_store.get("last_sentiment", {})
            tone = last_sentiment.get("sentiment", "calm")  # default to "calm"
        except ValueError as e:
            logger.warning(f"Invalid voice input: {e}")
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400

        try:
            speak(response, tone=tone)  # 🎤 pass tone into TTS
            speech_status = "success"
        except RuntimeError as e:
            logger.error(f"Speech synthesis failed: {e}")
            speech_status = f"failed: {str(e)}"

        return jsonify({
            "heard": user_input,
            "response": response,
            "tone": tone,
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
    
@app.route("/checkin", methods=["GET", "POST", "DELETE"])
def checkin():
    global checkin_state

    # GET => status
    if request.method == "GET":
        return jsonify({
            "active": checkin_state.active,
            "phase": checkin_state.phase,
            "summary": checkin_state.summary
        }), 200

    # DELETE => cancel
    if request.method == "DELETE":
        checkin_state = CheckInState()  # reset
        return jsonify({"ok": True, "active": False}), 200

    # POST => start or progress the flow
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()

    # start if inactive or no user input provided
    if not checkin_state.active and not user_input:
        checkin_state = CheckInState(active=True, phase="intro")
        return jsonify({
            "active": True,
            "phase": checkin_state.phase,
            "reply": "Let’s do a quick check-in. How are you feeling right now?"
        }), 200

    # progress the flow
    new_state, reply, done = handle_checkin_input(checkin_state, user_input)
    checkin_state = new_state
    if done:
        # optional: persist summary via ren_agent.memory_store if you want
        checkin_state = CheckInState()  # reset after wrap

    return jsonify({
        "active": checkin_state.active,
        "phase": checkin_state.phase,
        "reply": reply,
        "done": done
    }), 200

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
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)