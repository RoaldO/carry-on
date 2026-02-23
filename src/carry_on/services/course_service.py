"""CourseService application service for course operations."""

from decimal import Decimal

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
        slope_rating: Decimal | None = None,
        course_rating: Decimal | None = None,
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

        course = Course.create(
            name=name,
            holes=hole_objects,
            slope_rating=slope_rating,
            course_rating=course_rating,
        )
        return self._repository.save(course, user_id)

    def get_course_detail(self, course_id: str, user_id: str) -> Course | None:
        """Get a specific course with full details.

        Args:
            course_id: The ID of the course to retrieve.
            user_id: The user requesting the course.

        Returns:
            The Course if found and owned by user, None otherwise.
        """
        return self._repository.find_by_id(CourseId(value=course_id), user_id)

    def get_user_courses(self, user_id: str) -> list[Course]:
        """Get courses for a user.

        Args:
            user_id: The user whose courses to retrieve.

        Returns:
            List of courses owned by the user.
        """
        return self._repository.find_by_user(user_id)
