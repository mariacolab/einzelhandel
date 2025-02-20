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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
