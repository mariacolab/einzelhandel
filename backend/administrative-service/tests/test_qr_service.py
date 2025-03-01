import requests

BASE_URL = 'http://localhost:5024'

def test_generate_qr_code():
    url = f"{BASE_URL}/generate"
    payload = {"data": "Hello World"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200, "QR-Code-Erzeugung schlug fehl."
    # Beispiel: Überprüfen, ob der Content-Type auf ein Bildformat hinweist
    assert response.headers.get('Content-Type') in ['image/png', 'image/jpeg'], "Unerwarteter Content-Type."
