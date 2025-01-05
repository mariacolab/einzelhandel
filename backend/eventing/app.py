from flask import Flask, jsonify

from common.middleware import token_required, role_required
from producer import send_message
import asyncio

app = Flask(__name__)

@token_required
@role_required('admin')
@app.route('/publish/<event>', methods=['POST'])
def publish_event(event):
    # Map event types to messages
    events = {
        "ImageUploaded": {"type": "ImageUploaded", "data": {"filename": "example.jpg"}},
        "ImageValidated": {"type": "ImageValidated", "data": {"status": "valid"}},
        "ClassificationCompleted": {"type": "ClassificationCompleted", "data": {"result": "cat"}},
        "QRCodeGenerated": {"type": "QRCodeGenerated", "data": {"code": "123456"}},
    }
    if event not in events:
        return jsonify({"error": "Event not recognized"}), 400

    asyncio.run(send_message(events[event]))
    return jsonify({"status": f"Event {event} published successfully."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)