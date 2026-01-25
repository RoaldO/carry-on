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


class TestShotsEndpoint:
    """Tests for shots API endpoints."""

    def test_get_shots_without_auth_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """GET /api/shots without authentication should return 401."""
        response = client.get("/api/shots")
        assert response.status_code == 401

    def test_get_shots_with_invalid_credentials_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """GET /api/shots with invalid credentials should return 401."""
        response = client.get(
            "/api/shots", headers={"X-Email": "wrong@example.com", "X-Pin": "wrong"}
        )
        assert response.status_code == 401

    def test_get_shots_with_valid_auth(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_shots_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/shots with valid authentication should return shots."""
        response = client.get("/api/shots", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "shots" in data
        assert "count" in data

    def test_post_shot_without_auth_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """POST /api/shots without authentication should return 401."""
        response = client.post(
            "/api/shots",
            json={"club": "i7", "distance": 150},
        )
        assert response.status_code == 401

    def test_post_shot_with_valid_auth(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_shots_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/shots with valid authentication should create shot."""
        response = client.post(
            "/api/shots",
            json={"club": "i7", "distance": 150},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Shot recorded successfully"
        assert data["shot"]["club"] == "i7"
        assert data["shot"]["distance"] == 150

    def test_post_failed_shot(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_shots_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/shots with fail=true should not require distance."""
        response = client.post(
            "/api/shots",
            json={"club": "d", "fail": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["shot"]["fail"] is True
        assert data["shot"]["distance"] is None

    def test_post_shot_without_distance_or_fail_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_shots_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/shots without distance and fail=false should return 400."""
        response = client.post(
            "/api/shots",
            json={"club": "i7"},
            headers=auth_headers,
        )
        assert response.status_code == 400
