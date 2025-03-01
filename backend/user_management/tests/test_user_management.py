import requests

BASE_URL = 'http://localhost:5022'

def test_create_user():
    url = f"{BASE_URL}/users"
    payload = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 201, "User wurde nicht korrekt erstellt."
    data = response.json()
    assert "id" in data, "Antwort enthält keine User-ID."

def test_get_users():
    url = f"{BASE_URL}/users"
    response = requests.get(url)
    assert response.status_code == 200, "Abrufen der User-Liste schlug fehl."
    data = response.json()
    assert isinstance(data, list), "Die Antwort sollte eine Liste von Nutzern sein."
