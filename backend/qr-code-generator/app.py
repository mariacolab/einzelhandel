from flask import Flask, jsonify, request
from qrcode import save_qr_code_in_database
from common.middleware import token_required

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to the QR Code Service"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/qrcode', methods=['POST'])
@token_required
def add_product():
    data = request.json
    token = data.get("token")
    image_blob = data.get("image_blob")
    encrypted_data = data.get("encrypted_data")
    qrcode = save_qr_code_in_database(token, image_blob, encrypted_data)
    if qrcode:
        return jsonify({"id": qrcode.id}), 201
    return jsonify({"error": "Product could not be created"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
