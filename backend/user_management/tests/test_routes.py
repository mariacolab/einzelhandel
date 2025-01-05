import unittest
from unittest.mock import patch
from flask_jwt_extended import create_access_token
from ..app import app
from backend.user_management.auth import hash_password


class TestRoutes(unittest.TestCase):

    @patch('routes.requests.post')
    def test_register(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"message": "User created"}
        client = app.test_client()
        # Token erstellen
        with app.test_request_context():
            token = create_access_token(identity={"id": 1, "username": "testuser"})

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post('/auth/register', headers=headers, json={
            "username": "testuser",
            "password": "testpassword"
        })
        self.assertEqual(response.status_code, 201)

    @patch('routes.requests.get')  # Mock für requests.get
    def test_login(self, mock_get):
        # Simuliere die Antwort von database-management
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,
            "username": "testuser",
            "password": hash_password("testpassword")
        }

        client = app.test_client()

        # Führe den Login-Test durch
        response = client.post('/auth/login', json={
            "username": "testuser",
            "password": "testpassword"
        })

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request') # Mock für requests.post
    def test_logout(self, mock_verify_jwt):
        # Simuliere die Antwort
        #mock_post.return_value.status_code = 200
        #mock_post.return_value.json.return_value = {"message": "Logged out successfully"}
        mock_verify_jwt.return_value = True
        client = app.test_client()

        #with app.test_request_context():
        #    token = create_access_token(identity={"id": 1, "username": "testuser"})

        # Logout-Endpunkt aufrufen
        #headers = {"Authorization": f"Bearer {token}"}
        headers = {"Authorization": "Bearer mocked_token"}
        response = client.post('/auth/logout', headers=headers)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Logged out successfully"})
