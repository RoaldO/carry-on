"""Tests for CarryOn API endpoints."""

from unittest.mock import MagicMock, patch

import allure
from fastapi.testclient import TestClient

from carry_on.api.pin_security import hash_pin, AuthenticatedUser


@allure.feature("REST API")
@allure.story("Authentication")
class TestVerifyPinReturnsAuthenticatedUser:
    """Tests for verify_pin returning AuthenticatedUser."""

    def test_verify_pin_returns_authenticated_user(self) -> None:
        """verify_pin should return AuthenticatedUser with user data."""
        from carry_on.api.index import verify_pin

        test_email = "test@example.com"
        test_pin = "1234"
        mock_user = {
            "_id": "user123",
            "email": test_email,
            "display_name": "Test User",
            "pin_hash": hash_pin(test_pin),
            "activated_at": "2026-01-25T10:00:00Z",
        }

        with patch("carry_on.api.index.get_users_collection") as mock_get_collection:
            mock_collection = MagicMock()
            mock_collection.find_one.return_value = mock_user
            mock_get_collection.return_value = mock_collection

            result = verify_pin(x_pin=test_pin, x_email=test_email)

            assert isinstance(result, AuthenticatedUser)
            assert result.id == "user123"
            assert result.email == test_email
            assert result.display_name == "Test User"

    def test_verify_pin_returns_user_without_display_name(self) -> None:
        """verify_pin should handle users without display_name."""
        from carry_on.api.index import AuthenticatedUser, verify_pin

        test_email = "test@example.com"
        test_pin = "1234"
        mock_user = {
            "_id": "user456",
            "email": test_email,
            "pin_hash": hash_pin(test_pin),
            "activated_at": "2026-01-25T10:00:00Z",
        }

        with patch("carry_on.api.index.get_users_collection") as mock_get_collection:
            mock_collection = MagicMock()
            mock_collection.find_one.return_value = mock_user
            mock_get_collection.return_value = mock_collection

            result = verify_pin(x_pin=test_pin, x_email=test_email)

            assert isinstance(result, AuthenticatedUser)
            assert result.id == "user456"
            assert result.display_name == ""


@allure.feature("REST API")
@allure.story("Root Endpoint")
class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_html(self, client: TestClient) -> None:
        """Root endpoint should return HTML form."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "CarryOn" in response.text


@allure.feature("REST API")
@allure.story("Strokes API")
class TestStrokesEndpoint:
    """Tests for strokes API endpoints."""

    def test_get_strokes_without_auth_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """GET /api/strokes without authentication should return 401."""
        response = client.get("/api/strokes")
        assert response.status_code == 401

    def test_get_strokes_with_invalid_credentials_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """GET /api/strokes with invalid credentials should return 401."""
        response = client.get(
            "/api/strokes", headers={"X-Email": "wrong@example.com", "X-Pin": "wrong"}
        )
        assert response.status_code == 401

    def test_get_strokes_with_valid_auth(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_strokes_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes with valid authentication should return strokes."""
        response = client.get("/api/strokes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "strokes" in data
        assert "count" in data

    def test_post_stroke_without_auth_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """POST /api/strokes without authentication should return 401."""
        response = client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
        )
        assert response.status_code == 401

    def test_post_stroke_with_valid_auth(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_strokes_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes with valid authentication should create stroke."""
        response = client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Stroke recorded successfully"
        assert data["stroke"]["club"] == "7i"
        assert data["stroke"]["distance"] == 150

    def test_post_failed_stroke(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_strokes_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes with fail=true should not require distance."""
        response = client.post(
            "/api/strokes",
            json={"club": "d", "fail": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stroke"]["fail"] is True
        assert data["stroke"]["distance"] is None

    def test_post_stroke_without_distance_or_fail_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_strokes_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes without distance and fail=false should return 400."""
        response = client.post(
            "/api/strokes",
            json={"club": "7i"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_post_stroke_stores_user_id(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_strokes_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes should store user_id in the document."""
        response = client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify insert_one was called with user_id
        call_args = mock_strokes_collection.insert_one.call_args
        inserted_doc = call_args[0][0]
        assert "user_id" in inserted_doc
        assert inserted_doc["user_id"] == "user123"

    def test_get_strokes_filters_by_user_id(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_strokes_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes should filter by user_id."""
        response = client.get("/api/strokes", headers=auth_headers)
        assert response.status_code == 200

        # Verify find was called with user_id filter
        call_args = mock_strokes_collection.find.call_args
        filter_query = call_args[0][0] if call_args[0] else call_args[1].get("filter")
        assert filter_query == {"user_id": "user123"}


@allure.feature("REST API")
@allure.story("Profile API")
class TestMeEndpoint:
    """Tests for /api/me endpoint."""

    def test_get_me_without_auth_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """GET /api/me without authentication should return 401."""
        response = client.get("/api/me")
        assert response.status_code == 401

    def test_get_me_with_valid_auth(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/me with valid authentication should return user info."""
        response = client.get("/api/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"

    def test_get_me_with_invalid_credentials_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """GET /api/me with invalid credentials should return 401."""
        response = client.get(
            "/api/me", headers={"X-Email": "wrong@example.com", "X-Pin": "wrong"}
        )
        assert response.status_code == 401
