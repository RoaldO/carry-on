"""Tests for CourseService."""

from unittest.mock import MagicMock

import allure
import pytest

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.repositories.course_repository import CourseRepository
from carry_on.domain.course.value_objects.hole import Hole
from carry_on.services.course_service import CourseService


def _sample_holes_dicts(n: int) -> list[dict]:
    """Helper to create a list of raw hole dicts for n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4, 4, 4, 3, 5, 4, 3, 4, 5, 4]
    return [
        {"hole_number": i + 1, "par": pars[i % len(pars)], "stroke_index": i + 1}
        for i in range(n)
    ]


@allure.feature("Application Services")
@allure.story("Course Service")
class TestCourseServiceInit:
    """Tests for CourseService initialization."""

    def test_init_accepts_repository(self) -> None:
        """CourseService should accept a repository in constructor."""
        repository = MagicMock(spec=CourseRepository)
        service = CourseService(repository)
        assert service._repository is repository


@allure.feature("Application Services")
@allure.story("Course Service")
class TestCourseServiceAddCourse:
    """Tests for CourseService.add_course() method."""

    def test_add_course_returns_course_id(self) -> None:
        """Should return CourseId from repository."""
        repository = MagicMock(spec=CourseRepository)
        expected_id = CourseId(value="course-123")
        repository.save.return_value = expected_id
        service = CourseService(repository)

        result = service.add_course(
            user_id="user123",
            name="Test Course",
            holes=_sample_holes_dicts(9),
        )

        assert result == expected_id

    def test_add_course_saves_correct_course(self) -> None:
        """Should create and save a Course with correct attributes."""
        repository = MagicMock(spec=CourseRepository)
        repository.save.return_value = CourseId(value="course-123")
        service = CourseService(repository)

        service.add_course(
            user_id="user123",
            name="Pitch & Putt",
            holes=_sample_holes_dicts(9),
        )

        repository.save.assert_called_once()
        course, user_id = repository.save.call_args[0]

        assert isinstance(course, Course)
        assert course.name == "Pitch & Putt"
        assert course.number_of_holes == 9
        assert user_id == "user123"

    def test_add_course_converts_hole_dicts_to_value_objects(self) -> None:
        """Should convert raw hole dicts to Hole value objects."""
        repository = MagicMock(spec=CourseRepository)
        repository.save.return_value = CourseId(value="course-123")
        service = CourseService(repository)

        holes = [
            {"hole_number": 1, "par": 3, "stroke_index": 1},
            {"hole_number": 2, "par": 4, "stroke_index": 2},
            {"hole_number": 3, "par": 5, "stroke_index": 3},
            {"hole_number": 4, "par": 4, "stroke_index": 4},
            {"hole_number": 5, "par": 3, "stroke_index": 5},
            {"hole_number": 6, "par": 4, "stroke_index": 6},
            {"hole_number": 7, "par": 4, "stroke_index": 7},
            {"hole_number": 8, "par": 5, "stroke_index": 8},
            {"hole_number": 9, "par": 4, "stroke_index": 9},
        ]
        service.add_course(user_id="user123", name="Test", holes=holes)

        course, _ = repository.save.call_args[0]
        assert all(isinstance(h, Hole) for h in course.holes)
        assert course.holes[0].par == 3
        assert course.holes[2].par == 5

    def test_add_18_hole_course(self) -> None:
        """Should support 18-hole courses."""
        repository = MagicMock(spec=CourseRepository)
        repository.save.return_value = CourseId(value="course-456")
        service = CourseService(repository)

        result = service.add_course(
            user_id="user123",
            name="Championship Course",
            holes=_sample_holes_dicts(18),
        )

        assert result == CourseId(value="course-456")
        course, _ = repository.save.call_args[0]
        assert course.number_of_holes == 18

    def test_add_course_with_invalid_name_raises_value_error(self) -> None:
        """Should raise ValueError for empty course name."""
        repository = MagicMock(spec=CourseRepository)
        service = CourseService(repository)

        with pytest.raises(ValueError, match="Course name required"):
            service.add_course(
                user_id="user123",
                name="",
                holes=_sample_holes_dicts(9),
            )

        repository.save.assert_not_called()

    def test_add_course_with_wrong_hole_count_raises_value_error(self) -> None:
        """Should raise ValueError for invalid number of holes."""
        repository = MagicMock(spec=CourseRepository)
        service = CourseService(repository)

        with pytest.raises(ValueError, match="Course must have exactly 9 or 18 holes"):
            service.add_course(
                user_id="user123",
                name="Bad Course",
                holes=_sample_holes_dicts(7),
            )

        repository.save.assert_not_called()


@allure.feature("Application Services")
@allure.story("Course Service")
class TestCourseServiceGetCourseDetail:
    """Tests for CourseService.get_course_detail() method."""

    def test_get_course_detail_returns_course(self) -> None:
        """Should return Course when found by repository."""
        repository = MagicMock(spec=CourseRepository)
        pars = [4, 4, 3, 5, 4, 3, 4, 5, 4]
        holes = tuple(
            Hole(hole_number=i + 1, par=pars[i], stroke_index=i + 1) for i in range(9)
        )
        expected_course = Course.create(
            name="Test Course", holes=holes, id=CourseId(value="c1")
        )
        repository.find_by_id.return_value = expected_course
        service = CourseService(repository)

        result = service.get_course_detail("c1", "user123")

        assert result is not None
        assert result.name == "Test Course"
        repository.find_by_id.assert_called_once_with(CourseId(value="c1"), "user123")

    def test_get_course_detail_returns_none_when_not_found(self) -> None:
        """Should return None when repository returns None."""
        repository = MagicMock(spec=CourseRepository)
        repository.find_by_id.return_value = None
        service = CourseService(repository)

        result = service.get_course_detail("nonexistent", "user123")

        assert result is None


@allure.feature("Application Services")
@allure.story("Course Service")
class TestCourseServiceGetUserCourses:
    """Tests for CourseService.get_user_courses() method."""

    def test_get_user_courses_delegates_to_repository(self) -> None:
        """Should delegate to repository with correct user_id."""
        repository = MagicMock(spec=CourseRepository)
        expected_courses: list[Course] = []
        repository.find_by_user.return_value = expected_courses
        service = CourseService(repository)

        result = service.get_user_courses("user123")

        assert result == expected_courses
        repository.find_by_user.assert_called_once_with("user123")

    def test_get_user_courses_returns_courses(self) -> None:
        """Should return courses from repository."""
        repository = MagicMock(spec=CourseRepository)
        pars = [4, 4, 3, 5, 4, 3, 4, 5, 4]
        holes = tuple(
            Hole(hole_number=i + 1, par=pars[i], stroke_index=i + 1) for i in range(9)
        )
        expected_courses = [
            Course.create(name="Test Course", holes=holes, id=CourseId(value="c1")),
        ]
        repository.find_by_user.return_value = expected_courses
        service = CourseService(repository)

        result = service.get_user_courses("user123")

        assert len(result) == 1
        assert result[0].name == "Test Course"

    def test_get_user_courses_returns_empty_list_when_no_courses(self) -> None:
        """Should return empty list when user has no courses."""
        repository = MagicMock(spec=CourseRepository)
        repository.find_by_user.return_value = []
        service = CourseService(repository)

        result = service.get_user_courses("user123")

        assert result == []
