# von Maria  Schuster
import logging
import os

import redis
from flask import Flask, jsonify, session
from flask_session import Session
from common.config import Config
from process_uploads import process_files

app = Flask(__name__)
app.config.from_object(Config)  # Lade zentrale Config

# Initialisiere Flask-Session
Session(app)


@app.route("/debug/session", methods=["GET"])
def debug_session():
    return jsonify(dict(session))


@app.route("/")
def home():
    return "Welcome to the Administrative Service"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
