import logging
import requests
from cryptography.fernet import Fernet

from common.utils import load_secrets

logging.basicConfig(level=logging.DEBUG)

try:
    secrets = load_secrets()
    key = secrets.get('ENCRYPTION_KEY')
    logging.debug(f"Loaded password: {key}")
except Exception as e:
    logging.error(f"Error loading secrets: {e}")
    raise


def save_qr_code_in_database(token: str, image_blob: bytes, encrypted_data: str):
    # TODO ins Backend verlagern und ein weiteres Event zum senden an Backend
    url = " http://nginx-proxy/database-management/qrcodes"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"{token}"
    }
    logging.info(f"Data: {headers}")
    data = {
        "type": "ProcessQrcode",
        "data": {
            "code": image_blob
        }
    }
    logging.info(f"Data: {data}")

    # POST-Anfrage senden
    response = requests.post(url, headers=headers, json=data)
    logging.info(f"Response: {response.request}")
    logging.info(f"Response: {response.status_code}")
    qr_data = response.json()
    qr_id = qr_data.get("id")

    if not key:
        raise ValueError("ENCRYPTION_KEY not found in .env file")

    # Initialisiere den Fernet-Verschlüsselungsalgorithmus
    cipher = Fernet(key)

    # Entschlüsseln der Daten
    decrypted_data = cipher.decrypt(encrypted_data)
    print("Entschlüsselte Daten:", decrypted_data.decode())
    product_id = decrypted_data.get("id")
    name = decrypted_data.get("name")
    description = decrypted_data.get("description")
    price = decrypted_data.get("price")

    url = f"http://nginx-proxy/database-management/products/{product_id}"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"{token}"
    }
    logging.info(f"Data: {headers}")
    data = {
        "name": name,
        "description": description,
        "price": price,
        "qr_code_id": qr_id,
    }
    logging.info(f"Data: {data}")

    # POST-Anfrage senden
    response = requests.put(url, headers=headers, json=data)
    logging.info(f"Response: {response.request}")
    logging.info(f"Response: {response.status_code}")

    return qr_id
