import os
import redis
from common.utils import load_secrets
from common import JSONSerializer


class Config:
    """ Allgemeine Konfiguration für alle Microservices """

    DEBUG = True

    # Lade Secrets
    secrets = load_secrets()
    SECRET_KEY = secrets.get('SECRET_KEY', 'fallback_secret_key')
    JWT_SECRET_KEY = secrets.get('JWT_SECRET_KEY', 'fallback_jwt_key')

    # Redis Konfiguration
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    # Session-Konfiguration
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'flask_session:'
    SESSION_COOKIE_SECURE = False  # Setze auf True, wenn HTTPS genutzt wird
    SESSION_COOKIE_HTTPONLY = True  # Schutz vor JavaScript-Zugriff
    SESSION_COOKIE_SAMESITE = 'Lax'  # Cookie-Kompatibilität für API-Aufrufe

    # Redis für Sessions
    SESSION_REDIS = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=False,
        password=REDIS_PASSWORD
    )

    # Stelle sicher, dass JSON zur Serialisierung verwendet wird
    SESSION_SERIALIZATION = JSONSerializer
