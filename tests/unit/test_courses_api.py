"""Tests for courses API using dependency injection."""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from tests.fakes.fake_course_repository import FakeCourseRepository
from tests.unit.conftest import TEST_USER_ID


def _sample_holes(n: int) -> list[dict]:
    """Helper to create a list of raw hole dicts for n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4, 4, 4, 3, 5, 4, 3, 4, 5, 4]
    return [
        {"hole_number": i + 1, "par": pars[i % len(pars)], "stroke_index": i + 1}
        for i in range(n)
    ]


@allure.feature("REST API")
@allure.story("Courses API")
class TestCoursesWithDependencyInjection:
    """Tests for courses endpoints using DI with fake repository."""

    def test_post_course_saves_to_repository(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/courses should save course via injected repository."""
        response = client.post(
            "/api/courses",
            json={"name": "Pitch & Putt", "holes": _sample_holes(9)},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Course created successfully"
        assert "id" in data

        # Verify course was saved to the fake repository
        assert len(override_course_repo.courses) == 1
        saved_course, user_id = override_course_repo.courses[0]
        assert saved_course.name == "Pitch & Putt"
        assert saved_course.number_of_holes == 9
        assert user_id == str(TEST_USER_ID)

    def test_post_18_hole_course(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/courses should support 18-hole courses."""
        response = client.post(
            "/api/courses",
            json={"name": "Championship", "holes": _sample_holes(18)},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert len(override_course_repo.courses) == 1
        saved_course, _ = override_course_repo.courses[0]
        assert saved_course.number_of_holes == 18

    def test_post_course_with_empty_name_returns_400(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/courses with empty name should return 400."""
        response = client.post(
            "/api/courses",
            json={"name": "", "holes": _sample_holes(9)},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert len(override_course_repo.courses) == 0

    def test_post_course_without_auth_returns_401(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/courses without auth should return 401."""
        response = client.post(
            "/api/courses",
            json={"name": "Test", "holes": _sample_holes(9)},
        )

        assert response.status_code == 401

    def test_get_courses_returns_saved_courses(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/courses should return courses from repository."""
        # Create two courses
        client.post(
            "/api/courses",
            json={"name": "Course A", "holes": _sample_holes(9)},
            headers=auth_headers,
        )
        client.post(
            "/api/courses",
            json={"name": "Course B", "holes": _sample_holes(18)},
            headers=auth_headers,
        )

        # Retrieve them
        response = client.get("/api/courses", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["courses"]) == 2

        names = [c["name"] for c in data["courses"]]
        assert "Course A" in names
        assert "Course B" in names

    def test_get_courses_returns_course_details(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/courses should include course metadata."""
        client.post(
            "/api/courses",
            json={"name": "Detailed Course", "holes": _sample_holes(9)},
            headers=auth_headers,
        )

        response = client.get("/api/courses", headers=auth_headers)

        assert response.status_code == 200
        course = response.json()["courses"][0]
        assert course["name"] == "Detailed Course"
        assert course["number_of_holes"] == 9
        assert "total_par" in course
        assert "id" in course

    def test_get_courses_filters_by_user(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/courses should only return courses for authenticated user."""
        # Create a course for authenticated user
        client.post(
            "/api/courses",
            json={"name": "My Course", "holes": _sample_holes(9)},
            headers=auth_headers,
        )

        # Manually add a course for different user
        from carry_on.domain.course.aggregates.course import Course
        from carry_on.domain.course.value_objects.hole import Hole

        pars = [4, 4, 3, 5, 4, 3, 4, 5, 4]
        holes = tuple(
            Hole(hole_number=i + 1, par=pars[i], stroke_index=i + 1) for i in range(9)
        )
        other_course = Course.create(name="Other Course", holes=holes)
        override_course_repo.save(other_course, user_id="other_user_456")

        # Verify both in repo
        assert len(override_course_repo.courses) == 2

        # GET should only return authenticated user's courses
        response = client.get("/api/courses", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["courses"][0]["name"] == "My Course"

    def test_get_courses_without_auth_returns_401(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        mock_users_collection: MagicMock,
    ) -> None:
        """GET /api/courses without auth should return 401."""
        response = client.get("/api/courses")

        assert response.status_code == 401

    def test_get_courses_returns_empty_list(
        self,
        client: TestClient,
        override_course_repo: FakeCourseRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/courses should return empty list when no courses exist."""
        response = client.get("/api/courses", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["courses"] == []
