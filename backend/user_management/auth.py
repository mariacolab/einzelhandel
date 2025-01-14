import bcrypt
from common.utils import load_pepper
from config import Config

def hash_password(password):
    salt = bcrypt.gensalt()
    pepper = Config.PEPPER
    hashed = bcrypt.hashpw((password + pepper).encode("utf-8"), salt)
    return hashed.decode("utf-8"), salt

def verify_password(stored_password, provided_password):
    pepper = load_pepper()
    return bcrypt.checkpw((provided_password + pepper).encode("utf-8"), stored_password.encode("utf-8"))

