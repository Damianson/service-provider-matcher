import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db, get_all_providers, get_providers_by_category, DB_PATH
from seed import seed
from matcher import match_and_rank_providers

# Load environment variables from root or backend directory
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
backend_env = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
if os.path.exists(root_env):
    load_dotenv(root_env)
if os.path.exists(backend_env):
    load_dotenv(backend_env)
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Locate static folder for production React build
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if not os.path.exists(STATIC_DIR):
    # If Docker container copied dist directly to backend/static
    STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

app = Flask(__name__, static_folder=STATIC_DIR if os.path.exists(STATIC_DIR) else None)
CORS(app)

# Ensure database exists and is seeded on startup
def ensure_database():
    if not os.path.exists(DB_PATH):
        logger.info("Initializing and seeding database...")
        seed()
    else:
        init_db()

ensure_database()

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "service-provider-matcher",
        "version": "1.0.0"
    })

@app.route("/api/config", methods=["GET"])
def get_config():
    gemini_key = os.getenv("GEMINI_API_KEY")
    return jsonify({
        "has_gemini": bool(gemini_key),
        "engine_name": "Gemini AI Engine",
        "categories": ["plumber", "electrician", "cleaner", "tutor"],
        "availability_options": [
            {"value": "any", "label": "Any / Flexible"},
            {"value": "weekdays", "label": "Weekdays"},
            {"value": "weekends", "label": "Weekends"},
            {"value": "evenings", "label": "Evenings"},
            {"value": "emergency", "label": "Urgent / Emergency (24/7)"}
        ]
    })

@app.route("/api/providers", methods=["GET"])
def list_providers():
    category = request.args.get("category")
    if category:
        providers = get_providers_by_category(category)
    else:
        providers = get_all_providers()
    return jsonify({
        "count": len(providers),
        "providers": providers
    })

@app.route("/api/seed", methods=["POST"])
def reseed():
    seed()
    return jsonify({"status": "reseeded", "count": len(get_all_providers())})

@app.route("/api/match", methods=["POST"])
def match_providers():
    data = request.get_json() or {}
    category = data.get("category", "").strip().lower()
    
    if not category:
        return jsonify({"error": "Category is required (plumber, electrician, cleaner, tutor)"}), 400
        
    all_providers = get_all_providers()
    ai_pref = data.get("ai_preference", "auto")
    
    result = match_and_rank_providers(
        all_providers=all_providers,
        client_request=data,
        ai_preference=ai_pref
    )
    
    return jsonify(result)

# Production Frontend Serving
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if app.static_folder and os.path.exists(app.static_folder):
        file_path = os.path.join(app.static_folder, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")
    return jsonify({
        "message": "Service Provider Matcher API running. Build frontend into frontend/dist or run frontend dev server on port 5173.",
        "endpoints": ["/api/health", "/api/config", "/api/providers", "/api/match"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

