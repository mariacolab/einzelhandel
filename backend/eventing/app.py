import logging

from flask import Flask, jsonify

from common.middleware import token_required, role_required
from producer import send_message
import asyncio

app = Flask(__name__)
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)


@app.route('/publish/<event>', methods=['POST'])
@token_required
@role_required('Admin', 'Mitarbeiter', 'Kunde')
def publish_event(event):
    # Map event types to messages
    try:
        logging.debug(f"Processing event: {event}")

        events = {
            "ImageUploaded": {"type": "ImageUploaded", "data": {"filename": "example.jpg"}},
            "ImageValidated": {"type": "ImageValidated", "data": {"status": "valid"}},
            "ClassificationCompleted": {"type": "ClassificationCompleted", "data": {"result": "cat"}},
            "QRCodeGenerated": {"type": "QRCodeGenerated", "data": {"code": "123456"}},
        }
        if event not in events:
            logging.debug("Event not recognized")
            return jsonify({"error": "Event not recognized"}), 400

        asyncio.run(send_message(events[event]))
        logging.debug(f"Event {event} published successfully")
        return jsonify({"status": f"Event {event} published successfully."}), 200

    except Exception as e:
        logging.debug(f"Error in publish_event: {e}")
        return jsonify({"message": "Internal server error", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
