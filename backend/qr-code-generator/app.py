from flask import Flask, jsonify, request
from common.middleware import token_required

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to the QR Code Service"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
