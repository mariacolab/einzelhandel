import logging
import os
import redis
from flask import Flask, jsonify
from flask_session import Session

from common.config import Config

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
    return "Welcome to the Frontend"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
