"""Tests for CarryOn API endpoints."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_html(self, client: TestClient) -> None:
        """Root endpoint should return HTML form."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "CarryOn" in response.text


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
            json={"club": "i7", "distance": 150},
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
            json={"club": "i7", "distance": 150},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Stroke recorded successfully"
        assert data["stroke"]["club"] == "i7"
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
            json={"club": "i7"},
            headers=auth_headers,
        )
        assert response.status_code == 400
