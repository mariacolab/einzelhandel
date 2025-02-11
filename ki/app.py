import logging
from flask import Flask, jsonify, request
from flask_session import Session

from common.config import Config
from common.middleware import token_required, role_required

app = Flask(__name__)
# app.config['DEBUG'] = True
# logging.basicConfig(level=logging.DEBUG)
# redis_password = os.getenv("REDIS_PASSWORD", None)
#
# redis_client = redis.StrictRedis(
#     host='redis',
#     port=6379,
#     db=0,
#     decode_responses=True,
#     password=redis_password  # Passwort setzen
# )
app.config.from_object(Config)  # Lade zentrale Config

# Initialisiere Flask-Session
Session(app)

@app.route("/")
def home():
    return "Welcome to the KI"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/ai/start-task', methods=['POST'])
@token_required
@role_required('Admin')
def start_ai_task():
    if 'images' not in request.files:
        return jsonify({"error": "Keine Bilder hochgeladen"}), 400

    files = {'images': request.files.getlist('images')}
    # TODO start des Nachtest aufrufen

    if len(files) >= 1:
        return jsonify({"status": "KI-Lauf gestartet"}), 202
    return jsonify({"error": "Fehler beim Starten des KI-Laufs"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
