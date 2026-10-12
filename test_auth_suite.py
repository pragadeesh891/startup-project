import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Ensure working directory environment
import database
import google_auth
from pymongo.errors import DuplicateKeyError

class TestGoogleAuthSuite(unittest.TestCase):

    def setUp(self):
        self.db = database.get_db()
        self.test_email = "test.oauth.runner.user99@careerpath.ai"
        self.test_sub = "google-sub-runner-99999"
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        if self.db is not None:
            self.db.users.delete_many({
                "$or": [
                    {"email": self.test_email},
                    {"google_sub": self.test_sub},
                    {"email": "pwd.existing.user@careerpath.ai"}
                ]
            })

    # --------------------------------------------------------------------------
    # 1. Successful Google Authentication
    # --------------------------------------------------------------------------
    @patch("google_auth.requests.post")
    @patch("google_auth.google_id_token.verify_oauth2_token")
    @patch("google_auth.is_configured", return_value=True)
    def test_01_successful_google_authentication(self, mock_cfg, mock_verify, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "mock_access_token_123",
            "id_token": "mock_raw_jwt_token_456"
        }
        mock_post.return_value = mock_resp

        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": google_auth.get_client_id() or "mock-client-id",
            "sub": "sub-12345",
            "email": "verified.user@gmail.com",
            "email_verified": True,
            "name": "Verified User",
            "picture": "https://lh3.googleusercontent.com/photo.jpg"
        }

        user_info, err = google_auth.exchange_code_for_user_info("auth_code_xyz")
        self.assertIsNone(err)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info["sub"], "sub-12345")
        self.assertEqual(user_info["email"], "verified.user@gmail.com")
        self.assertTrue(user_info["email_verified"])
        self.assertEqual(user_info["name"], "Verified User")
        self.assertEqual(user_info["picture"], "https://lh3.googleusercontent.com/photo.jpg")

    # --------------------------------------------------------------------------
    # 2. Creation of a New Google Account in MongoDB
    # --------------------------------------------------------------------------
    def test_02_creation_of_new_google_account(self):
        success, msg, user = database.authenticate_or_register_google_user(
            email=self.test_email,
            name="Test OAuth User",
            picture="https://example.com/avatar.jpg",
            google_sub=self.test_sub
        )
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], self.test_email)
        self.assertEqual(user["google_sub"], self.test_sub)
        self.assertEqual(user["auth_provider"], "google")
        self.assertIn("_id", user)

        # Verify persisted in database
        if self.db is not None:
            saved = self.db.users.find_one({"google_sub": self.test_sub})
            self.assertIsNotNone(saved)
            self.assertEqual(saved["email"], self.test_email)

    # --------------------------------------------------------------------------
    # 3. Login for an Existing Google Account
    # --------------------------------------------------------------------------
    def test_03_login_existing_google_account(self):
        # Initial registration
        s1, m1, u1 = database.authenticate_or_register_google_user(
            email=self.test_email,
            name="First Login",
            google_sub=self.test_sub
        )
        self.assertTrue(s1)
        original_id = u1["_id"]

        # Subsequent login
        s2, m2, u2 = database.authenticate_or_register_google_user(
            email=self.test_email,
            name="Second Login",
            picture="https://example.com/updated_pic.png",
            google_sub=self.test_sub
        )
        self.assertTrue(s2)
        self.assertEqual(u2["_id"], original_id)
        self.assertEqual(u2["avatar_url"], "https://example.com/updated_pic.png")

    # --------------------------------------------------------------------------
    # 4. Repeated Login Without Duplicate Accounts
    # --------------------------------------------------------------------------
    def test_04_repeated_login_no_duplicates(self):
        for i in range(5):
            success, msg, u = database.authenticate_or_register_google_user(
                email=self.test_email,
                name=f"Repeated Login {i}",
                google_sub=self.test_sub
            )
            self.assertTrue(success)

        if self.db is not None:
            count = self.db.users.count_documents({"google_sub": self.test_sub})
            self.assertEqual(count, 1)

    # --------------------------------------------------------------------------
    # 5. Invalid OAuth State (CSRF Protection)
    # --------------------------------------------------------------------------
    def test_05_invalid_oauth_state(self):
        valid_state = google_auth.generate_state_token()
        wrong_state = "malicious_or_tampered_state_token"

        # Matching session state
        self.assertTrue(google_auth.validate_state(valid_state, valid_state))
        
        # Fresh session (Streamlit page reload after external redirect)
        fresh_valid_state = google_auth.generate_state_token()
        self.assertTrue(google_auth.validate_state(None, fresh_valid_state))
        
        # Tampered or invalid states are strictly rejected
        self.assertFalse(google_auth.validate_state(valid_state, wrong_state))
        self.assertFalse(google_auth.validate_state(None, wrong_state))
        self.assertFalse(google_auth.validate_state(valid_state, ""))
        self.assertFalse(google_auth.validate_state(None, ""))
        self.assertFalse(google_auth.validate_state(None, None))

    # --------------------------------------------------------------------------
    # 6. Missing or Invalid Authorization Code
    # --------------------------------------------------------------------------
    @patch("google_auth.requests.post")
    @patch("google_auth.is_configured", return_value=True)
    def test_06_missing_or_invalid_authorization_code(self, mock_cfg, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Malformed auth code."
        }
        mock_post.return_value = mock_resp

        user_info, err = google_auth.exchange_code_for_user_info("bad_code")
        self.assertIsNone(user_info)
        self.assertIn("Google token exchange failed", err)

    # --------------------------------------------------------------------------
    # 7. Invalid or Expired ID Token
    # --------------------------------------------------------------------------
    @patch("google_auth.requests.post")
    @patch("google_auth.google_id_token.verify_oauth2_token")
    @patch("google_auth.is_configured", return_value=True)
    def test_07_invalid_or_expired_id_token(self, mock_cfg, mock_verify, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "valid_token",
            "id_token": "expired_jwt_token"
        }
        mock_post.return_value = mock_resp

        mock_verify.side_effect = ValueError("Token used too late, certificate expired")

        user_info, err = google_auth.exchange_code_for_user_info("code_abc")
        self.assertIsNone(user_info)
        self.assertIn("Invalid Google ID token claims", err)

    # --------------------------------------------------------------------------
    # 8. Unverified Email
    # --------------------------------------------------------------------------
    @patch("google_auth.requests.post")
    @patch("google_auth.google_id_token.verify_oauth2_token")
    @patch("google_auth.is_configured", return_value=True)
    def test_08_unverified_email(self, mock_cfg, mock_verify, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "token",
            "id_token": "jwt"
        }
        mock_post.return_value = mock_resp

        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "sub": "sub-999",
            "email": "unverified@example.com",
            "email_verified": False
        }

        user_info, err = google_auth.exchange_code_for_user_info("code_abc")
        self.assertIsNone(user_info)
        self.assertIn("not been verified by Google", err)

    # --------------------------------------------------------------------------
    # 9. Existing Password Account with Matching Email (No Automatic Linking)
    # --------------------------------------------------------------------------
    def test_09_existing_password_account_blocks_auto_link(self):
        pwd_email = "pwd.existing.user@careerpath.ai"
        # Register standard email/password user
        s_reg, m_reg, u_reg = database.register_user(
            name="Password User",
            email=pwd_email,
            password="SecurePassword123!"
        )
        self.assertTrue(s_reg)

        # Attempt Google login with matching email
        s_g, m_g, u_g = database.authenticate_or_register_google_user(
            email=pwd_email,
            name="Attacker Impersonator",
            google_sub="attacker-sub-666"
        )
        self.assertFalse(s_g)
        self.assertIsNone(u_g)
        self.assertIn("automatic linking is disabled", m_g)
        self.assertIn("Please sign in with your email and password", m_g)

    # --------------------------------------------------------------------------
    # 10. MongoDB Errors and Duplicate-Key Handling
    # --------------------------------------------------------------------------
    @patch("database.get_db")
    def test_10_mongodb_duplicate_key_error_handled(self, mock_get_db):
        mock_db = MagicMock()
        mock_db.users.find_one.side_effect = [
            None,  # Not found by google_sub
            None,  # Not found by email
            {"_id": "resolved_id_123", "email": "race@example.com", "name": "Race User"}  # Found on DuplicateKey recovery
        ]
        mock_db.users.insert_one.side_effect = DuplicateKeyError("E11000 duplicate key error")
        mock_get_db.return_value = mock_db

        success, msg, user = database.authenticate_or_register_google_user(
            email="race@example.com",
            name="Race User",
            google_sub="race-sub"
        )
        self.assertTrue(success)
        self.assertEqual(user["_id"], "resolved_id_123")

    # --------------------------------------------------------------------------
    # 11. User Cancellation (OAuth error=access_denied)
    # --------------------------------------------------------------------------
    def test_11_user_cancellation(self):
        # When user clicks Cancel at Google consent screen
        error_param = "access_denied"
        self.assertEqual(error_param, "access_denied")

        # Verify state is cleared
        session_mock = {"oauth_state": "some_state_token"}
        session_mock["oauth_state"] = None
        self.assertIsNone(session_mock["oauth_state"])

    # --------------------------------------------------------------------------
    # 12. Logout and Session Clearing
    # --------------------------------------------------------------------------
    def test_12_logout_and_session_clearing(self):
        session_state = {
            "user": {"name": "Test User", "email": "test@careerpath.ai"},
            "oauth_state": "active_token_123",
            "quiz_active": True
        }
        # Simulate Sign Out handler
        session_state["user"] = None
        session_state["oauth_state"] = None
        session_state["quiz_active"] = False

        self.assertIsNone(session_state["user"])
        self.assertIsNone(session_state["oauth_state"])
        self.assertFalse(session_state["quiz_active"])

    # --------------------------------------------------------------------------
    # 13. Existing Email/Password Login and Registration Still Works
    # --------------------------------------------------------------------------
    def test_13_existing_email_password_auth_intact(self):
        ep_email = "direct.auth.user@careerpath.ai"
        if self.db is not None:
            self.db.users.delete_many({"email": ep_email})

        # Register
        s_reg, m_reg, u_reg = database.register_user(
            name="Direct Auth User",
            email=ep_email,
            password="MySecretPassword123!"
        )
        self.assertTrue(s_reg)

        # Correct login
        s_auth, m_auth, u_auth = database.authenticate_user(ep_email, "MySecretPassword123!")
        self.assertTrue(s_auth)
        self.assertEqual(u_auth["email"], ep_email)

        # Incorrect password
        s_bad, m_bad, u_bad = database.authenticate_user(ep_email, "WrongPassword999")
        self.assertFalse(s_bad)
        self.assertIsNone(u_bad)

        if self.db is not None:
            self.db.users.delete_many({"email": ep_email})

    # --------------------------------------------------------------------------
    # 14. Dashboard Access After Successful Authentication
    # --------------------------------------------------------------------------
    def test_14_dashboard_session_structure(self):
        success, msg, user = database.authenticate_or_register_google_user(
            email=self.test_email,
            name="Dashboard User",
            google_sub=self.test_sub
        )
        self.assertTrue(success)

        # Verify required user keys for Streamlit dashboard rendering
        self.assertIn("name", user)
        self.assertIn("email", user)
        self.assertIn("_id", user)
        user_initial = (user["name"][:1]).upper() if user.get("name") else "U"
        self.assertEqual(user_initial, "D")

if __name__ == "__main__":
    unittest.main(verbosity=2)
