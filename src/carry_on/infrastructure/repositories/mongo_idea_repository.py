"""MongoDB implementation of IdeaRepository."""

from datetime import UTC, datetime
from typing import NotRequired, TypedDict, TypeGuard, TypeVar

from bson.objectid import ObjectId
from pymongo.collection import Collection

from carry_on.domain.entities.idea import Idea, IdeaId


class IdeaDoc(TypedDict):
    _id: NotRequired[ObjectId]
    description: str
    created_at: str
    user_id: str


T = TypeVar("T")


def is_not_none(value: T | None) -> TypeGuard[T]:
    return value is not None


class MongoIdeaRepository:
    """MongoDB implementation of the IdeaRepository protocol.

    Maps domain entities to/from MongoDB documents and handles
    persistence operations.
    """

    def __init__(self, collection: Collection[IdeaDoc]) -> None:
        """Initialize repository with MongoDB collection.

        Args:
            collection: The MongoDB collection for storing ideas.
        """
        self._collection = collection

    def save(self, idea: Idea, user_id: str) -> IdeaId:
        """Save an idea and return its ID.

        Args:
            idea: The idea entity to save.
            user_id: The ID of the user who owns this idea.

        Returns:
            The IdeaId of the saved idea.
        """
        doc = self._to_document(idea, user_id)
        result = self._collection.insert_one(doc)
        return IdeaId(value=str(result.inserted_id))

    def _to_document(self, idea: Idea, user_id: str) -> IdeaDoc:
        """Map domain entity to MongoDB document.

        Args:
            idea: The idea entity to convert.
            user_id: The ID of the user who owns this idea.

        Returns:
            Dictionary suitable for MongoDB insertion.
        """
        return {
            "description": idea.description,
            "created_at": datetime.now(UTC).isoformat(),
            "user_id": user_id,
        }
