"""MongoDB implementation of CourseRepository."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import NotRequired, TypedDict

from bson.objectid import ObjectId
from pymongo.collection import Collection

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.value_objects.hole import Hole


class HoleDoc(TypedDict):
    hole_number: int
    par: int
    stroke_index: int


class CourseDoc(TypedDict):
    _id: NotRequired[ObjectId]
    name: str
    holes: list[HoleDoc]
    slope_rating: NotRequired[str | None]
    course_rating: NotRequired[str | None]
    created_at: str
    user_id: str


class MongoCourseRepository:
    """MongoDB implementation of the CourseRepository protocol.

    Maps domain aggregates to/from MongoDB documents and handles
    persistence operations.
    """

    def __init__(self, collection: Collection[CourseDoc]) -> None:
        """Initialize repository with MongoDB collection.

        Args:
            collection: The MongoDB collection for storing courses.
        """
        self._collection = collection

    def save(self, course: Course, user_id: str) -> CourseId:
        """Save a course and return its ID.

        Args:
            course: The course aggregate to save.
            user_id: The ID of the user who owns this course.

        Returns:
            The CourseId of the saved course.
        """
        doc = self._to_document(course, user_id)
        result = self._collection.insert_one(doc)
        return CourseId(value=str(result.inserted_id))

    def find_by_id(self, course_id: CourseId, user_id: str) -> Course | None:
        """Find a course by ID for a specific user.

        Args:
            course_id: The ID of the course to find.
            user_id: The ID of the user who owns the course.

        Returns:
            The Course aggregate if found, None otherwise.
        """
        doc = self._collection.find_one(
            {"_id": ObjectId(course_id.value), "user_id": user_id}
        )
        if doc is None:
            return None
        return self._to_entity(doc)

    def find_by_user(self, user_id: str) -> list[Course]:
        """Find courses for a user.

        Args:
            user_id: The ID of the user whose courses to find.

        Returns:
            List of Course aggregates owned by the user.
        """
        cursor = self._collection.find({"user_id": user_id})
        return [self._to_entity(doc) for doc in cursor]

    def _to_document(self, course: Course, user_id: str) -> CourseDoc:
        """Map domain aggregate to MongoDB document."""
        return {
            "name": course.name,
            "holes": [
                {
                    "hole_number": h.hole_number,
                    "par": h.par,
                    "stroke_index": h.stroke_index,
                }
                for h in course.holes
            ],
            "slope_rating": (
                str(course.slope_rating) if course.slope_rating is not None else None
            ),
            "course_rating": (
                str(course.course_rating) if course.course_rating is not None else None
            ),
            "created_at": datetime.now(UTC).isoformat(),
            "user_id": user_id,
        }

    def _to_entity(self, doc: CourseDoc) -> Course:
        """Map MongoDB document to domain aggregate."""
        holes = tuple(
            Hole(
                hole_number=h["hole_number"],
                par=h["par"],
                stroke_index=h["stroke_index"],
            )
            for h in doc["holes"]
        )
        raw_slope = doc.get("slope_rating")
        raw_cr = doc.get("course_rating")
        return Course.create(
            name=doc["name"],
            holes=holes,
            id=CourseId(value=str(doc["_id"])),
            slope_rating=(Decimal(raw_slope) if raw_slope is not None else None),
            course_rating=(Decimal(raw_cr) if raw_cr is not None else None),
        )
