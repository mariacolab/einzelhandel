import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_FILE = os.path.join(BASE_DIR, "secrets", "github_credentials.txt")

def load_secrets():
    """Lädt alle Secrets aus der Datei."""
    secrets = {}
    with open(SECRET_FILE, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                secrets[key] = value
    return secrets

def load_pepper():
    """Lädt nur die Pepper aus den Secrets."""
    secrets = load_secrets()
    return secrets.get("PEPPER")