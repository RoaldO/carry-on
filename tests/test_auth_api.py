"""Tests for Authentication API endpoints (multi-user support)."""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from carry_on.api.pin_security import hash_pin


@allure.feature("REST API")
@allure.story("Authentication")
class TestCheckEmailEndpoint:
    """Tests for POST /api/check-email endpoint."""

    def test_check_email_not_found(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/check-email with unknown email returns 404."""
        mock_users_collection.find_one.return_value = None

        response = client.post(
            "/api/check-email",
            json={"email": "unknown@example.com"},
        )
        assert response.status_code == 404

    def test_check_email_not_activated(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/check-email with non-activated user returns needs_activation."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/check-email",
            json={"email": "user@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "needs_activation"
        assert data["display_name"] == "Test User"

    def test_check_email_activated(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/check-email with activated user returns activated."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": "hashed_pin",
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/check-email",
            json={"email": "user@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "activated"
        assert data["display_name"] == "Test User"


@allure.feature("REST API")
@allure.story("Authentication")
class TestActivateEndpoint:
    """Tests for POST /api/activate endpoint."""

    def test_activate_unknown_email_returns_404(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/activate with unknown email returns 404."""
        mock_users_collection.find_one.return_value = None

        response = client.post(
            "/api/activate",
            json={"email": "unknown@example.com", "pin": "1234"},
        )
        assert response.status_code == 404

    def test_activate_already_activated_returns_400(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/activate with already activated user returns 400."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "pin_hash": "already_set",
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/activate",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 400

    def test_activate_success(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/activate with valid email sets PIN and activates."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/activate",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account activated successfully"
        assert data["user"]["email"] == "user@example.com"
        mock_users_collection.update_one.assert_called_once()

    def test_activate_hashes_pin(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/activate stores PIN as Argon2 hash."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/activate",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 200
        # Verify the stored hash is Argon2 format
        call_args = mock_users_collection.update_one.call_args
        stored_hash = call_args[0][1]["$set"]["pin_hash"]
        assert stored_hash.startswith("$argon2id$")


@allure.feature("REST API")
@allure.story("Authentication")
class TestLoginEndpoint:
    """Tests for POST /api/login endpoint."""

    def test_login_unknown_email_returns_401(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with unknown email returns 401."""
        mock_users_collection.find_one.return_value = None

        response = client.post(
            "/api/login",
            json={"email": "unknown@example.com", "pin": "1234"},
        )
        assert response.status_code == 401

    def test_login_not_activated_returns_400(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with non-activated user returns 400."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "pin_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 400

    def test_login_wrong_pin_returns_401(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with wrong PIN returns 401."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": "hashed_5678",  # Different from input
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 401

    def test_login_success_with_hashed_pin(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with correct credentials and hashed PIN returns success."""
        hashed = hash_pin("1234")
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == "user@example.com"
        # Should not rehash since PIN is already properly hashed
        mock_users_collection.update_one.assert_not_called()

    def test_login_success_with_plain_pin_triggers_rehash(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with plain text PIN triggers rehashing."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": "1234",  # Plain text PIN (legacy)
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "pin": "1234"},
        )
        assert response.status_code == 200
        # Should trigger rehash since PIN was plain text
        mock_users_collection.update_one.assert_called_once()
        # Verify the new hash is Argon2 format
        call_args = mock_users_collection.update_one.call_args
        new_hash = call_args[0][1]["$set"]["pin_hash"]
        assert new_hash.startswith("$argon2id$")
