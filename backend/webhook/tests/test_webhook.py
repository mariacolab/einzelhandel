import requests

BASE_URL = 'http://localhost:5028'

def test_webhook_processing():
    url = f"{BASE_URL}/webhook"
    payload = {
        "event": "test_event",
        "data": {"key": "value"}
    }
    response = requests.post(url, json=payload)
    assert response.status_code in [200, 201], "Webhook-Verarbeitung schlug fehl."
