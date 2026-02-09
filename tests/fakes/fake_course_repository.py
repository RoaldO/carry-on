"""In-memory fake implementation of CourseRepository for testing."""

from uuid import uuid4

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.repositories.course_repository import CourseRepository


class FakeCourseRepository(CourseRepository):
    """In-memory implementation of CourseRepository for testing.

    Stores courses in memory and provides the same interface as the
    real MongoDB repository, enabling tests without database access.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._courses: list[tuple[Course, str]] = []  # (course, user_id)

    def save(self, course: Course, user_id: str) -> CourseId:
        """Save a course and return its ID.

        Args:
            course: The course aggregate to save.
            user_id: The ID of the user who owns this course.

        Returns:
            The CourseId of the saved course.
        """
        course_id = CourseId(value=str(uuid4()))
        saved_course = Course.create(
            name=course.name,
            holes=course.holes,
            id=course_id,
        )
        self._courses.append((saved_course, user_id))
        return course_id

    def find_by_user(self, user_id: str) -> list[Course]:
        """Find courses for a user.

        Args:
            user_id: The ID of the user whose courses to find.

        Returns:
            List of Course aggregates owned by the user.
        """
        return [course for course, uid in self._courses if uid == user_id]

    def clear(self) -> None:
        """Clear all stored courses. Useful for test setup/teardown."""
        self._courses.clear()

    @property
    def courses(self) -> list[tuple[Course, str]]:
        """Get all stored courses with their user IDs for test assertions."""
        return list(self._courses)
