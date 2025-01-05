import unittest
from backend.user_management.auth import hash_password, verify_password

class TestAuth(unittest.TestCase):

    def test_hash_password(self):
        password = "mypassword"
        hashed = hash_password(password)
        self.assertTrue(verify_password(hashed, password))

    def test_verify_password(self):
        password = "mypassword"
        hashed = hash_password(password)
        self.assertTrue(verify_password(hashed, password))
        self.assertFalse(verify_password(hashed, "wrongpassword"))
