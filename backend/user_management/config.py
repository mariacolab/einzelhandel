import os
from umutils import load_secrets

class Config:
    secrets = load_secrets()
    SECRET_KEY = secrets.get("SECRET_KEY")
    JWT_SECRET_KEY = secrets.get("JWT_SECRET_KEY")
    DATABASE_URL = "http://database-management-service:5000"
    PEPPER = secrets.get("PEPPER")


class TestConfig(Config):
    secrets = load_secrets()
    SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"
    DEBUG = True
    TESTING = True
    SECRET_KEY = secrets.get("SECRET_KEY")
