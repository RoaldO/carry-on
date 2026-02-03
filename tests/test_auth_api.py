"""Tests for Authentication API endpoints (multi-user support)."""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from carry_on.api.password_security import hash_password


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
            "password_hash": None,
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
            "password_hash": "hashed_pin",
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
            json={"email": "unknown@example.com", "password": "SecurePass1"},
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
            "password_hash": "already_set",
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/activate",
            json={"email": "user@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 400

    def test_activate_success(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/activate with valid email sets password and activates."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/activate",
            json={"email": "user@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account activated successfully"
        assert data["user"]["email"] == "user@example.com"
        mock_users_collection.update_one.assert_called_once()

    def test_activate_hashes_password(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/activate stores password as Argon2 hash."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/activate",
            json={"email": "user@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 200
        # Verify the stored hash is Argon2 format
        call_args = mock_users_collection.update_one.call_args
        stored_hash = call_args[0][1]["$set"]["password_hash"]
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
            json={"email": "unknown@example.com", "password": "1234"},
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
            "password_hash": None,
            "activated_at": None,
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "password": "1234"},
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
            "password_hash": "hashed_5678",  # Different from input
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "password": "1234"},
        )
        assert response.status_code == 401

    def test_login_success_with_hashed_password(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with hashed password returns success."""
        hashed = hash_password("1234")
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "password": "1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == "user@example.com"
        # Should not rehash since password is already properly hashed
        mock_users_collection.update_one.assert_not_called()

    def test_login_success_with_plain_password_triggers_rehash(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with plain text password triggers rehashing."""
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": "1234",  # Plain text password (legacy)
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "password": "1234"},
        )
        assert response.status_code == 200
        # Should trigger rehash since password was plain text
        mock_users_collection.update_one.assert_called_once()
        # Verify the new hash is Argon2 format
        call_args = mock_users_collection.update_one.call_args
        new_hash = call_args[0][1]["$set"]["password_hash"]
        assert new_hash.startswith("$argon2id$")

    def test_login_with_weak_password_returns_password_update_required(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with weak password returns password_update_required status."""
        hashed = hash_password("1234")  # 4-char weak password
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "password": "1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "password_update_required"
        assert data["user"]["email"] == "user@example.com"

    def test_login_with_compliant_password_returns_success(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with compliant password returns success status."""
        hashed = hash_password("SecurePass123")  # 13-char compliant password
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/login",
            json={"email": "user@example.com", "password": "SecurePass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user"]["email"] == "user@example.com"


@allure.feature("REST API")
@allure.story("Password Update")
class TestUpdatePasswordEndpoint:
    """Tests for POST /api/update-password endpoint."""

    def test_update_password_with_wrong_current_password_returns_401(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/update-password with wrong current password returns 401."""
        hashed = hash_password("1234")
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/update-password",
            json={
                "email": "user@example.com",
                "current_password": "wrong",
                "new_password": "SecurePass123",
            },
        )
        assert response.status_code == 401

    def test_update_password_with_weak_new_password_returns_400(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/update-password with weak new password returns 400."""
        hashed = hash_password("1234")
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/update-password",
            json={
                "email": "user@example.com",
                "current_password": "1234",
                "new_password": "short",  # Only 5 chars
            },
        )
        assert response.status_code == 400

    def test_update_password_unknown_email_returns_404(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/update-password with unknown email returns 404."""
        mock_users_collection.find_one.return_value = None

        response = client.post(
            "/api/update-password",
            json={
                "email": "unknown@example.com",
                "current_password": "1234",
                "new_password": "SecurePass123",
            },
        )
        assert response.status_code == 404

    def test_update_password_success(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/update-password with valid data updates password."""
        hashed = hash_password("1234")
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "password_hash": hashed,
            "activated_at": "2026-01-25T10:00:00Z",
        }

        response = client.post(
            "/api/update-password",
            json={
                "email": "user@example.com",
                "current_password": "1234",
                "new_password": "SecurePass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Password updated successfully"

        # Verify the new hash is Argon2 format
        mock_users_collection.update_one.assert_called_once()
        call_args = mock_users_collection.update_one.call_args
        new_hash = call_args[0][1]["$set"]["password_hash"]
        assert new_hash.startswith("$argon2id$")
