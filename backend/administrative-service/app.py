import logging

from flask import Flask, jsonify
from process_uploads import process_files

app = Flask(__name__)
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def home():
    return "Welcome to the Administrative Service"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
