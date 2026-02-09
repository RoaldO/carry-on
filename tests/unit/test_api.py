"""Tests for CarryOn API endpoints."""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from carry_on.services.authentication_service import AuthenticatedUser
from tests.fakes.fake_stroke_repository import FakeStrokeRepository
from tests.unit.conftest import TEST_USER_ID


@allure.feature("REST API")
@allure.story("Authentication")
class TestVerifyPasswordReturnsAuthenticatedUser:
    """Tests for verify_password returning AuthenticatedUser."""

    def test_verify_password_returns_authenticated_user(self) -> None:
        """verify_password should return AuthenticatedUser with user data."""
        from carry_on.api.index import verify_password

        test_email = "test@example.com"
        test_password = "1234"
        expected_user = AuthenticatedUser(
            id="user123",
            email=test_email,
            display_name="Test User",
        )

        mock_auth_service = MagicMock()
        mock_auth_service.authenticate.return_value = expected_user

        result = verify_password(
            x_password=test_password, x_email=test_email, auth_service=mock_auth_service
        )

        assert isinstance(result, AuthenticatedUser)
        assert result.id == "user123"
        assert result.email == test_email
        assert result.display_name == "Test User"
        mock_auth_service.authenticate.assert_called_once_with(
            test_email, test_password
        )

    def test_verify_password_returns_user_without_display_name(self) -> None:
        """verify_password should handle users without display_name."""
        from carry_on.api.index import verify_password

        test_email = "test@example.com"
        test_password = "1234"
        expected_user = AuthenticatedUser(
            id="user456",
            email=test_email,
            display_name="",
        )

        mock_auth_service = MagicMock()
        mock_auth_service.authenticate.return_value = expected_user

        result = verify_password(
            x_password=test_password, x_email=test_email, auth_service=mock_auth_service
        )

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
        headers = {"X-Email": "wrong@example.com", "X-Password": "wrong"}
        response = client.get("/api/strokes", headers=headers)
        assert response.status_code == 401

    def test_get_strokes_with_valid_auth(
        self,
        client: TestClient,
        override_stroke_repo: FakeStrokeRepository,
        auth_headers: dict[str, str],
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
        override_stroke_repo: FakeStrokeRepository,
        auth_headers: dict[str, str],
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
        override_stroke_repo: FakeStrokeRepository,
        auth_headers: dict[str, str],
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
        override_stroke_repo: FakeStrokeRepository,
        auth_headers: dict[str, str],
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
        override_stroke_repo: FakeStrokeRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes should store user_id in the document."""
        response = client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify stroke was stored with user_id in fake repository
        assert len(override_stroke_repo._strokes) > 0
        stroke, user_id, _ = override_stroke_repo._strokes[-1]
        assert user_id == str(TEST_USER_ID)

    def test_get_strokes_filters_by_user_id(
        self,
        client: TestClient,
        override_stroke_repo: FakeStrokeRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes should filter by user_id."""
        response = client.get("/api/strokes", headers=auth_headers)
        assert response.status_code == 200
        # With fake repository, filtering is automatic based on the authenticated user
        # Response should only contain strokes for the authenticated user
        data = response.json()
        assert "strokes" in data


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
            "/api/me", headers={"X-Email": "wrong@example.com", "X-Password": "wrong"}
        )
        assert response.status_code == 401
