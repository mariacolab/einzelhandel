from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_security import Security
from auth import hash_password, verify_password
from umutils import load_secrets
from routes import register_routes
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

secrets = load_secrets()
app.config['SECRET_KEY'] = secrets.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = secrets.get('JWT_SECRET_KEY')

#print(f"Loaded SECRET_KEY: {app.config['SECRET_KEY']}")
#print(f"Loaded JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")

# Initialisiere JWT Manager
jwt = JWTManager(app)

# Initialisiere Flask-Security
security = Security(app)

# Registriere die REST-Schnittstellen
register_routes(app)


# Routes
@app.route('/')
def index():
    return "Hello, World!"


@app.route('/admin/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
