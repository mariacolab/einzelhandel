import requests
from flask import Flask, jsonify, request
from common.middleware import token_required

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to the QR Code Service"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

DATABASE_API_URL = "http://database-management-service:5001"

@app.route('/qrcode/scan/result', methods=['GET'])
def qrcode_scan_result():
    response = requests.get(f"{DATABASE_API_URL}/qrcodes")
    if response.status_code == 200:
        return jsonify(response.json()), 200
    return jsonify({"error": "QR-Codes nicht gefunden"}), 404

@app.route('/qrcode/information/<int:qrcode_id>', methods=['GET'])
def qrcode_information(qrcode_id):
    response = requests.get(f"{DATABASE_API_URL}/qrcodes/{qrcode_id}")
    if response.status_code == 200:
        return jsonify(response.json()), 200
    return jsonify({"error": "QR-Code nicht gefunden"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
