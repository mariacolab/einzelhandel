import requests

BASE_URL = 'http://localhost:5025'

def test_publish_event():
    url = f"{BASE_URL}/publish"
    payload = {
        "event": "user_created",
        "data": {"user_id": 123}
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 404, "Event konnte nicht veröffentlicht werden."
