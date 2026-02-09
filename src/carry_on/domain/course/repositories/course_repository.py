"""CourseRepository protocol defining the repository interface."""

from typing import Protocol, runtime_checkable

from carry_on.domain.course.aggregates.course import Course, CourseId


@runtime_checkable
class CourseRepository(Protocol):
    """Repository interface for Course aggregates.

    Defines the contract for course persistence operations.
    Implementations handle the actual storage mechanism (MongoDB, etc.).

    Note: user_id is passed as a parameter rather than stored in the aggregate
    because user ownership is a query/security concern, not part of the
    domain concept of a course.
    """

    def save(self, course: Course, user_id: str) -> CourseId:
        """Save a course and return its ID.

        Args:
            course: The course aggregate to save.
            user_id: The ID of the user who owns this course.

        Returns:
            The CourseId of the saved course.
        """

    def find_by_id(self, course_id: CourseId, user_id: str) -> Course | None:
        """Find a course by ID for a specific user.

        Args:
            course_id: The ID of the course to find.
            user_id: The ID of the user who owns the course.

        Returns:
            The Course aggregate if found, None otherwise.
        """

    def find_by_user(self, user_id: str) -> list[Course]:
        """Find courses for a user.

        Args:
            user_id: The ID of the user whose courses to find.

        Returns:
            List of Course aggregates owned by the user.
        """
