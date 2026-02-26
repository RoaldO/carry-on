"""Tests for rounds API using dependency injection."""

from decimal import Decimal
from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from carry_on.domain.course.value_objects.round_status import RoundStatus
from tests.fakes.fake_round_repository import FakeRoundRepository
from tests.unit.conftest import TEST_USER_ID


def _sample_holes(n: int) -> list[dict]:
    """Helper to create a list of raw hole result dicts for n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4]
    return [
        {
            "hole_number": i + 1,
            "strokes": 4,
            "par": pars[i % len(pars)],
            "stroke_index": i + 1,
        }
        for i in range(n)
    ]


@allure.feature("REST API")
@allure.story("Rounds API")
class TestRoundsWithDependencyInjection:
    """Tests for rounds endpoints using DI with fake repository."""

    def test_post_round_saves_to_repository(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds should save round via injected repository."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Round recorded successfully"
        assert "id" in data

        # Verify round was saved to the fake repository
        assert len(override_round_repo.rounds) == 1
        saved_round, user_id = override_round_repo.rounds[0]
        assert saved_round.course_name == "Pitch & Putt"
        assert len(saved_round.holes) == 9
        assert user_id == str(TEST_USER_ID)

    def test_post_round_with_empty_course_returns_400(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds with empty course should return 400."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_post_round_without_auth_returns_401(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/rounds without auth should return 401."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Test",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
        )

        assert response.status_code == 401

    def test_get_rounds_returns_saved_rounds(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should return rounds from repository."""
        # Create a round first
        client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )

        # Retrieve
        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["rounds"]) == 1
        assert data["rounds"][0]["course_name"] == "Pitch & Putt"

    def test_get_rounds_returns_empty_list(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should return empty list when no rounds exist."""
        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["rounds"] == []

    def test_get_rounds_without_auth_returns_401(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        mock_users_collection: MagicMock,
    ) -> None:
        """GET /api/rounds without auth should return 401."""
        response = client.get("/api/rounds")

        assert response.status_code == 401

    def test_post_round_with_empty_holes_succeeds(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds with empty holes should succeed for incremental workflow."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data

        # Verify round was saved with no holes
        assert len(override_round_repo.rounds) == 1
        saved_round, _ = override_round_repo.rounds[0]
        assert len(saved_round.holes) == 0

    def test_patch_hole_updates_single_hole(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH /api/rounds/{round_id}/holes/{hole_number} should update hole."""
        # Create a round first
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Update a hole
        response = client.patch(
            f"/api/rounds/{round_id}/holes/1",
            json={"strokes": 4, "par": 4, "stroke_index": 1},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Hole updated successfully"

        # Verify hole was saved
        saved_round, _ = override_round_repo.rounds[0]
        assert len(saved_round.holes) == 1
        assert saved_round.holes[0].hole_number == 1
        assert saved_round.holes[0].strokes == 4

    def test_patch_hole_returns_404_for_nonexistent_round(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH endpoint should return 404 for missing round."""
        response = client.patch(
            "/api/rounds/nonexistent/holes/1",
            json={"strokes": 4, "par": 4, "stroke_index": 1},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_round_by_id_returns_round_details(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{round_id} should return round with holes."""
        # Create a round with holes
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(2),
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Retrieve the round
        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == round_id
        assert data["course_name"] == "Pitch & Putt"
        assert data["date"] == "2026-02-01"
        assert len(data["holes"]) == 2
        assert data["is_complete"] is False

    def test_get_round_by_id_returns_404_for_nonexistent(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{round_id} should return 404 for missing round."""
        response = client.get("/api/rounds/nonexistent", headers=auth_headers)

        assert response.status_code == 404


@allure.feature("REST API")
@allure.story("Rounds API - Status")
class TestRoundsStatusAPI:
    """Tests for round status field in API responses and status update endpoint."""

    def test_get_rounds_includes_status_field(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should include status field in response."""
        # Create a round
        client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )

        # Retrieve rounds
        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["rounds"]) == 1
        assert "status" in data["rounds"][0]
        assert data["rounds"][0]["status"] == "ip"

    def test_get_round_by_id_includes_status_field(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{round_id} should include status field."""
        # Create a round
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Retrieve the round
        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ip"

    def test_patch_round_status_finish_succeeds(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH /api/rounds/{round_id}/status?action=finish should finish round."""
        # Create a round
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Finish the round
        response = client.patch(
            f"/api/rounds/{round_id}/status?action=finish",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Round status updated successfully"

        # Verify status was updated
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.status == RoundStatus.FINISHED

    def test_patch_round_status_abort_succeeds(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH /api/rounds/{round_id}/status?action=abort should abort round."""
        # Create a round
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Abort the round
        response = client.patch(
            f"/api/rounds/{round_id}/status?action=abort",
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify status was updated
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.status == RoundStatus.ABORTED

    def test_patch_round_status_resume_succeeds(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH /api/rounds/{round_id}/status?action=resume should resume round."""
        # Create and abort a round
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        client.patch(
            f"/api/rounds/{round_id}/status?action=abort",
            headers=auth_headers,
        )

        # Resume the round
        response = client.patch(
            f"/api/rounds/{round_id}/status?action=resume",
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify status was updated
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.status == RoundStatus.IN_PROGRESS

    def test_patch_round_status_invalid_action_returns_400(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH endpoint should return 400 for invalid action."""
        # Create a round
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Try invalid action
        response = client.patch(
            f"/api/rounds/{round_id}/status?action=invalid",
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_patch_round_status_nonexistent_round_returns_404(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH endpoint should return 404 for missing round."""
        response = client.patch(
            "/api/rounds/nonexistent/status?action=finish",
            headers=auth_headers,
        )

        assert response.status_code == 404


@allure.feature("REST API")
@allure.story("Rounds API - Slope & Course Rating")
class TestRoundsAPIRatings:
    """Tests for slope/course rating in rounds API."""

    def test_post_round_with_ratings(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds with ratings should store them."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Hilly Links",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
                "slope_rating": "125",
                "course_rating": "72.3",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.slope_rating == Decimal("125")
        assert saved_round.course_rating == Decimal("72.3")

    def test_post_round_without_ratings_defaults_to_none(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds without ratings defaults to None."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Old Course",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.slope_rating is None
        assert saved_round.course_rating is None


@allure.feature("REST API")
@allure.story("Rounds API - Course Handicap")
class TestRoundsAPICourseHandicap:
    """Tests for course_handicap in API responses."""

    def test_get_rounds_includes_course_handicap(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should include course_handicap in each round."""
        # Create and finish a round so course_handicap is computed
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]
        client.patch(
            f"/api/rounds/{round_id}/status?action=finish",
            headers=auth_headers,
        )

        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "course_handicap" in data["rounds"][0]

    def test_get_round_by_id_includes_course_handicap(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{id} should include course_handicap."""
        # Create and finish a round
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]
        client.patch(
            f"/api/rounds/{round_id}/status?action=finish",
            headers=auth_headers,
        )

        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "course_handicap" in data


@allure.feature("REST API")
@allure.story("Rounds API - Num Holes & Course Par")
class TestRoundsAPINumHolesCoursePar:
    """Tests for number_of_holes and course_par in rounds API."""

    def test_post_round_with_number_of_holes_and_course_par(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds with number_of_holes and course_par should store them."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Hilly Links",
                "date": "2026-02-01",
                "holes": [],
                "number_of_holes": 18,
                "course_par": 72,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.num_holes == 18
        assert saved_round.course_par == 72

    def test_get_round_by_id_includes_num_holes_and_course_par(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{id} should include num_holes and course_par."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Hilly Links",
                "date": "2026-02-01",
                "holes": [],
                "number_of_holes": 18,
                "course_par": 72,
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["num_holes"] == 18
        assert data["course_par"] == 72

    def test_get_rounds_list_includes_num_holes_and_course_par(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should include num_holes and course_par in list."""
        client.post(
            "/api/rounds",
            json={
                "course_name": "Hilly Links",
                "date": "2026-02-01",
                "holes": [],
                "number_of_holes": 9,
                "course_par": 36,
            },
            headers=auth_headers,
        )

        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["rounds"][0]["num_holes"] == 9
        assert data["rounds"][0]["course_par"] == 36


@allure.feature("REST API")
@allure.story("Rounds API - Per-Hole Stableford Points")
class TestRoundsAPIPerHoleStableford:
    """Tests for stableford_points per hole in API responses."""

    def test_get_round_by_id_includes_stableford_points_per_hole(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{id} should include stableford_points in each hole."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Hilly Links",
                "date": "2026-02-01",
                "holes": _sample_holes(2),
                "number_of_holes": 18,
                "course_par": 72,
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        for hole in data["holes"]:
            assert "stableford_points" in hole

    def test_get_round_by_id_includes_handicap_strokes_per_hole(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{id} should include handicap_strokes in each hole."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Hilly Links",
                "date": "2026-02-01",
                "holes": _sample_holes(2),
                "number_of_holes": 18,
                "course_par": 72,
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        for hole in data["holes"]:
            assert "handicap_strokes" in hole


@allure.feature("REST API")
@allure.story("Rounds API - Clubs Used")
class TestRoundsAPIClubsUsed:
    """Tests for clubs_used in rounds API."""

    def test_patch_hole_with_clubs_used(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH hole with clubs_used should save on domain object."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.patch(
            f"/api/rounds/{round_id}/holes/1",
            json={
                "strokes": 3,
                "par": 4,
                "stroke_index": 1,
                "clubs_used": ["d", "7i", "pw"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.holes[0].clubs_used == ("d", "7i", "pw")

    def test_patch_hole_without_clubs_used_defaults_to_none(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH hole without clubs_used should default to None."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.patch(
            f"/api/rounds/{round_id}/holes/1",
            json={"strokes": 4, "par": 4, "stroke_index": 1},
            headers=auth_headers,
        )

        assert response.status_code == 200
        saved_round, _ = override_round_repo.rounds[0]
        assert saved_round.holes[0].clubs_used is None

    def test_patch_hole_with_mismatched_clubs_used_returns_400(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH with mismatched strokes/clubs_used length should return 400."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.patch(
            f"/api/rounds/{round_id}/holes/1",
            json={
                "strokes": 2,
                "par": 4,
                "stroke_index": 1,
                "clubs_used": ["d", "7i", "pw"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_patch_hole_zero_strokes_empty_clubs(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """PATCH with strokes=0 and clubs_used=[] should succeed (in-progress)."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        response = client.patch(
            f"/api/rounds/{round_id}/holes/1",
            json={
                "strokes": 0,
                "par": 4,
                "stroke_index": 1,
                "clubs_used": [],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_get_round_includes_clubs_used_per_hole(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds/{id} should include clubs_used per hole."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Add a hole with clubs
        client.patch(
            f"/api/rounds/{round_id}/holes/1",
            json={
                "strokes": 2,
                "par": 3,
                "stroke_index": 1,
                "clubs_used": ["7i", "pw"],
            },
            headers=auth_headers,
        )

        response = client.get(f"/api/rounds/{round_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["holes"][0]["clubs_used"] == ["7i", "pw"]

    def test_finish_with_zero_stroke_hole_returns_400(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """Finish with an incomplete 0-stroke hole should return 400."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [],
            },
            headers=auth_headers,
        )
        round_id = response.json()["id"]

        # Add 8 complete holes + 1 zero-stroke hole
        for i in range(1, 9):
            client.patch(
                f"/api/rounds/{round_id}/holes/{i}",
                json={"strokes": 4, "par": 4, "stroke_index": i},
                headers=auth_headers,
            )
        client.patch(
            f"/api/rounds/{round_id}/holes/9",
            json={"strokes": 0, "par": 4, "stroke_index": 9},
            headers=auth_headers,
        )

        response = client.patch(
            f"/api/rounds/{round_id}/status?action=finish",
            headers=auth_headers,
        )

        assert response.status_code == 400
