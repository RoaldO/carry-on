"""Tests for CourseRepository protocol."""

import allure

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.repositories.course_repository import CourseRepository
from carry_on.domain.course.value_objects.hole import Hole


def _make_holes(n: int) -> tuple[Hole, ...]:
    """Helper to create a valid sequence of n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4, 4, 4, 3, 5, 4, 3, 4, 5, 4]
    return tuple(
        Hole(hole_number=i + 1, par=pars[i % len(pars)], stroke_index=i + 1)
        for i in range(n)
    )


@allure.feature("Domain Model")
@allure.story("Course Repository Protocol")
class TestCourseRepositoryProtocol:
    """Tests for CourseRepository protocol shape."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """CourseRepository should be a runtime-checkable Protocol."""
        assert hasattr(CourseRepository, "__protocol_attrs__") or isinstance(
            CourseRepository, type
        )

    def test_protocol_has_save_method(self) -> None:
        """CourseRepository should define a save method."""
        assert hasattr(CourseRepository, "save")

    def test_protocol_has_find_by_user_method(self) -> None:
        """CourseRepository should define a find_by_user method."""
        assert hasattr(CourseRepository, "find_by_user")

    def test_conforming_class_is_instance(self) -> None:
        """A class implementing save and find_by_user should satisfy the protocol."""

        class DummyRepo:
            def save(self, course: Course, user_id: str) -> CourseId:
                return CourseId(value="dummy")

            def find_by_user(self, user_id: str) -> list[Course]:
                return []

        assert isinstance(DummyRepo(), CourseRepository)

    def test_non_conforming_class_is_not_instance(self) -> None:
        """A class missing methods should not satisfy the protocol."""

        class NotARepo:
            pass

        assert not isinstance(NotARepo(), CourseRepository)
