import logging
from flask import Flask, jsonify, request
from flask_session import Session

from common.config import Config
from common.middleware import token_required, role_required
from detectYOLO11 import retrain
from rh_TF_Update import update_model_TF, prepare_Data

app = Flask(__name__)
app.config.from_object(Config)  # Lade zentrale Config

# Initialisiere Flask-Session
Session(app)

@app.route("/")
def home():
    return "Welcome to the KI"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/ai/tensorflow', methods=['POST'])
@token_required
@role_required('Admin')
def start_ai_task():
    if 'images' not in request.files:
        return jsonify({"error": "Keine Bilder hochgeladen"}), 400

    files = {'images': request.files.getlist('images')}
    labels =request.files.getlist('labels')
    # TODO start des Nachtest aufrufen
    update_model_TF()

    if len(files) >= 1:
        return jsonify({"status": "KI-Lauf Tensorflow gestartet"}), 202
    return jsonify({"error": "Fehler beim Starten des KI-Laufs"}), 404

@app.route('/ai/yolo', methods=['POST'])
@token_required
@role_required('Admin')
def start_ai_task():

    # TODO start des Nachtest aufrufen
    retrain()
    return jsonify({"status": "KI-Lauf Yolo gestartet"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
