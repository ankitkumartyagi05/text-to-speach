from flask import Flask, render_template, request, jsonify, send_from_directory, session
from gtts import gTTS
import os
import re
import hashlib
import base64
from io import BytesIO
from datetime import timedelta, datetime, timezone

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "text-to-speech-dev-secret")
app.permanent_session_lifetime = timedelta(minutes=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

MAX_CHARS = 5000
MAX_GENERATIONS_PER_SESSION = 5
SESSION_TIMEOUT_MINUTES = 30
AUDIO_CACHE = {}
AUDIO_CACHE_LIMIT = 12


def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)


def get_cached_audio(text, language):
    cache_key = f"{language}:{text}"
    return AUDIO_CACHE.get(cache_key)


def store_cached_audio(text, language, audio_data_url):
    cache_key = f"{language}:{text}"

    if len(AUDIO_CACHE) >= AUDIO_CACHE_LIMIT:
        first_key = next(iter(AUDIO_CACHE))
        AUDIO_CACHE.pop(first_key, None)

    AUDIO_CACHE[cache_key] = audio_data_url


def get_device_fingerprint():
    user_agent = request.headers.get("User-Agent", "")
    accept_language = request.headers.get("Accept-Language", "")
    remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    fingerprint_source = "|".join([user_agent, accept_language, remote_addr])
    return hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()


def reset_session_state():
    session.clear()
    session.permanent = True
    session["device_fingerprint"] = get_device_fingerprint()
    session["generated_count"] = 0
    session["started_at"] = datetime.now(timezone.utc).isoformat()


def ensure_session_state():
    session.permanent = True

    current_fingerprint = get_device_fingerprint()
    stored_fingerprint = session.get("device_fingerprint")

    if stored_fingerprint != current_fingerprint:
        reset_session_state()

    if "generated_count" not in session:
        session["generated_count"] = 0
        session["device_fingerprint"] = current_fingerprint
        session["started_at"] = datetime.now(timezone.utc).isoformat()

    return current_fingerprint


def get_session_state_payload():
    generated_count = session.get("generated_count", 0)
    remaining_generations = max(0, MAX_GENERATIONS_PER_SESSION - generated_count)
    started_at_raw = session.get("started_at")
    session_expires_in_minutes = SESSION_TIMEOUT_MINUTES

    if started_at_raw:
        started_at = datetime.fromisoformat(started_at_raw)
        expires_at = started_at + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        remaining_seconds = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        if remaining_seconds <= 0:
            return {
                "session_expired": True,
                "remaining_generations": MAX_GENERATIONS_PER_SESSION,
                "session_expires_in_minutes": SESSION_TIMEOUT_MINUTES,
            }

    return {
        "session_expired": False,
        "used_generations": generated_count,
        "remaining_generations": remaining_generations,
        "session_expires_in_minutes": session_expires_in_minutes,
        "device_fingerprint": session.get("device_fingerprint"),
    }


@app.route("/")
def home():
    ensure_session_state()
    return render_template("index.html")


@app.route("/style.css")
def style_css():
    return send_from_directory("templates", "style.css")


@app.route("/scripts.js")
def scripts_js():
    return send_from_directory("templates", "scripts.js")


@app.route("/session-status")
def session_status():
    ensure_session_state()
    return jsonify(get_session_state_payload())


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; media-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
    return response


@app.route("/generate-audio", methods=["POST", "OPTIONS"])
def generate_audio():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        ensure_session_state()
        generated_count = session.get("generated_count", 0)

        started_at_raw = session.get("started_at")
        if started_at_raw:
            started_at = datetime.fromisoformat(started_at_raw)
            session_expires_at = started_at + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
            if datetime.now(timezone.utc) >= session_expires_at:
                reset_session_state()
                return jsonify({
                    "error": "Session expired for this device. Reload the page to start a new session.",
                    "session_expired": True,
                    "remaining_generations": MAX_GENERATIONS_PER_SESSION,
                    "session_expires_in_minutes": SESSION_TIMEOUT_MINUTES,
                }), 440

        if generated_count >= MAX_GENERATIONS_PER_SESSION:
            return jsonify({
                "error": f"Generation limit reached. Maximum {MAX_GENERATIONS_PER_SESSION} audios per session."
            }), 429

        data = request.get_json()

        text = data.get("text", "").strip()
        filename = data.get("filename", "").strip()
        language = data.get("language", "en")

        if not text:
            return jsonify({"error": "Please enter text"}), 400

        if not filename:
            return jsonify({"error": "Please enter filename"}), 400

        if len(text) > MAX_CHARS:
            return jsonify({
                "error": f"Maximum {MAX_CHARS} characters allowed"
            }), 400

        filename = sanitize_filename(filename)

        cached_audio = get_cached_audio(text, language)

        if cached_audio:
            audio_data_url = cached_audio
        else:
            tts = gTTS(
                text=text,
                lang=language,
                slow=False
            )

            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_bytes = audio_buffer.getvalue()
            audio_data_url = "data:audio/mpeg;base64," + base64.b64encode(audio_bytes).decode("utf-8")
            store_cached_audio(text, language, audio_data_url)

        next_count = generated_count + 1
        session["generated_count"] = next_count
        download_name = f"{filename}_{next_count}.mp3"

        return jsonify({
            "success": True,
            "audio_data_url": audio_data_url,
            "download_name": download_name,
            "used_generations": next_count,
            "remaining_generations": MAX_GENERATIONS_PER_SESSION - next_count,
            "device_fingerprint": session.get("device_fingerprint"),
            "session_expires_in_minutes": SESSION_TIMEOUT_MINUTES,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)