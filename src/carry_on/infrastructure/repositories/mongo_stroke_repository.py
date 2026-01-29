"""MongoDB implementation of StrokeRepository."""

from datetime import UTC, date, datetime
from typing import NotRequired, TypedDict, TypeGuard, TypeVar

from bson.objectid import ObjectId
from pymongo.collection import Collection

from carry_on.domain.entities.stroke import Stroke, StrokeId
from carry_on.domain.value_objects.club_type import ClubType
from carry_on.domain.value_objects.distance import Distance
from carry_on.infrastructure.mongodb import get_database


class StrokeDoc(TypedDict):
    _id: NotRequired[ObjectId]
    club: str
    distance: int | None
    fail: bool
    date: str
    created_at: str
    user_id: str


T = TypeVar("T")


def is_not_none(value: T | None) -> TypeGuard[T]:
    return value is not None


class MongoStrokeRepository:
    """MongoDB implementation of the StrokeRepository protocol.

    Maps domain entities to/from MongoDB documents and handles
    persistence operations.
    """

    def __init__(self, collection: Collection[StrokeDoc]) -> None:
        """Initialize repository with MongoDB collection.

        Args:
            collection: The MongoDB collection for storing strokes.
        """
        self._collection = collection

    def save(self, stroke: Stroke, user_id: str) -> StrokeId:
        """Save a stroke and return its ID.

        Args:
            stroke: The stroke entity to save.
            user_id: The ID of the user who owns this stroke.

        Returns:
            The StrokeId of the saved stroke.
        """
        doc = self._to_document(stroke, user_id)
        result = self._collection.insert_one(doc)
        return StrokeId(value=str(result.inserted_id))

    def find_by_user(self, user_id: str, limit: int = 20) -> list[Stroke]:
        """Find strokes for a user, newest first.

        Args:
            user_id: The ID of the user whose strokes to find.
            limit: Maximum number of strokes to return (default 20).

        Returns:
            List of Stroke entities, ordered by creation time descending.
        """
        cursor = (
            self._collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [self._to_entity(doc) for doc in cursor]

    def _to_document(self, stroke: Stroke, user_id: str) -> StrokeDoc:
        """Map domain entity to MongoDB document.

        Args:
            stroke: The stroke entity to convert.
            user_id: The ID of the user who owns this stroke.

        Returns:
            Dictionary suitable for MongoDB insertion.
        """
        return {
            "club": stroke.club.value,
            "distance": stroke.distance.meters
            if is_not_none(stroke.distance)
            else None,
            "fail": stroke.fail,
            "date": stroke.stroke_date.isoformat(),
            "created_at": datetime.now(UTC).isoformat(),
            "user_id": user_id,
        }

    def _to_entity(self, doc: StrokeDoc) -> Stroke:
        """Map MongoDB document to domain entity.

        Args:
            doc: MongoDB document to convert.

        Returns:
            Stroke entity with data from the document.
        """
        optional_distance = doc.get("distance")
        is_not_none(optional_distance)
        distance = (
            Distance(meters=optional_distance)
            if is_not_none(optional_distance)
            else None
        )
        fail = doc.get("fail", False)
        created_at = (
            datetime.fromisoformat(doc["created_at"]) if doc.get("created_at") else None
        )

        if fail:
            return Stroke.create_failed(
                id=StrokeId(value=str(doc["_id"])),
                club=ClubType(doc["club"]),
                stroke_date=date.fromisoformat(doc["date"]),
                created_at=created_at,
            )
        else:
            return Stroke.create_successful(
                id=StrokeId(value=str(doc["_id"])),
                club=ClubType(doc["club"]),
                distance=distance,  # type: ignore[arg-type]
                stroke_date=date.fromisoformat(doc["date"]),
                created_at=created_at,
            )


def get_strokes_collection() -> Collection[StrokeDoc]:
    """Get MongoDB collection, initializing connection if needed."""
    return get_database().strokes
