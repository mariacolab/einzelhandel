from datetime import timedelta

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_session import Session

from common.middleware import role_required, token_required
from common.utils import load_secrets
from routes import register_routes
from config import Config

app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_object(Config)

secrets = load_secrets()
app.config['SECRET_KEY'] = secrets.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = secrets.get('JWT_SECRET_KEY')

# Session-Konfiguration
app.config['SESSION_TYPE'] = 'filesystem'  # Alternativen: 'redis', 'memcached', etc.
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Initialisiere Flask-Session
Session(app)

# Initialisiere JWT Manager
jwt = JWTManager(app)

# Registriere die REST-Schnittstellen
register_routes(app)


# Routes
@app.route('/')
def index():
    return "Hello, World!"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/admin', methods=['GET'])
@token_required
@role_required('Admin')
def admin_dashboard():
    return jsonify({"message": "Admin access granted"})


@app.route('/user', methods=['GET'])
@token_required
@role_required('Kunde')
def user_dashboard():
    return jsonify({"message": "User access granted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
