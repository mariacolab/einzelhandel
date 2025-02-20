from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Variable zur Steuerung von Watchdog
watchdog_active = False

@socketio.on('start_watchdog')
def start_watchdog():
    global watchdog_active
    watchdog_active = True
    logging.info("Watchdog aktiviert")

@socketio.on('stop_watchdog')
def stop_watchdog():
    global watchdog_active
    watchdog_active = False
    logging.info("Watchdog deaktiviert")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5011, debug=True)