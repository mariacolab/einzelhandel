import logging

import requests
from flask import Flask, jsonify, request

from common.middleware import token_required, role_required

app = Flask(__name__)
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)


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
