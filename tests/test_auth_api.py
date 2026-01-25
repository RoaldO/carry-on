"""Tests for Authentication API endpoints (multi-user support)."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient


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

    def test_login_success(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/login with correct credentials returns success."""
        # PIN "1234" hashed (we'll use simple comparison for now)
        mock_users_collection.find_one.return_value = {
            "_id": "user123",
            "email": "user@example.com",
            "display_name": "Test User",
            "pin_hash": "1234",  # Temporary: plain PIN until we add hashing
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
