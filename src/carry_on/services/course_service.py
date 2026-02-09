"""CourseService application service for course operations."""

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.repositories.course_repository import CourseRepository
from carry_on.domain.course.value_objects.hole import Hole


class CourseService:
    """Application service for course operations.

    Orchestrates course creation and retrieval, delegating
    persistence to the repository.
    """

    def __init__(self, repository: CourseRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The course repository for persistence operations.
        """
        self._repository = repository

    def add_course(
        self,
        user_id: str,
        name: str,
        holes: list[dict],
    ) -> CourseId:
        """Add a new golf course.

        Args:
            user_id: The user adding the course.
            name: Course name.
            holes: List of hole dicts with hole_number, par, stroke_index.

        Returns:
            The ID of the saved course.

        Raises:
            ValueError: If course data is invalid.
        """
        hole_objects = tuple(
            Hole(
                hole_number=h["hole_number"],
                par=h["par"],
                stroke_index=h["stroke_index"],
            )
            for h in holes
        )

        course = Course.create(name=name, holes=hole_objects)
        return self._repository.save(course, user_id)

    def get_user_courses(self, user_id: str) -> list[Course]:
        """Get courses for a user.

        Args:
            user_id: The user whose courses to retrieve.

        Returns:
            List of courses owned by the user.
        """
        return self._repository.find_by_user(user_id)
