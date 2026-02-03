"""MongoDB implementation of UserRepository."""

from datetime import datetime
from typing import NotRequired, TypedDict

from bson.objectid import ObjectId
from pymongo.collection import Collection

from carry_on.domain.entities.user import User, UserId
from carry_on.infrastructure.mongodb import get_database


class UserDoc(TypedDict):
    """TypedDict representing the MongoDB user document schema."""

    _id: NotRequired[ObjectId]
    email: str
    display_name: str
    password_hash: str | None
    activated_at: str | None


class MongoUserRepository:
    """MongoDB implementation of the UserRepository protocol.

    Maps domain entities to/from MongoDB documents and handles
    persistence operations.
    """

    def __init__(self, collection: Collection[UserDoc]) -> None:
        """Initialize repository with MongoDB collection.

        Args:
            collection: The MongoDB collection for storing users.
        """
        self._collection = collection

    def save(self, user: User) -> UserId:
        """Save a user and return its ID.

        For new users (id=None), creates a new record.
        For existing users, updates the record.

        Args:
            user: The user entity to save.

        Returns:
            The UserId of the saved user.
        """
        doc = self._to_document(user)

        if user.id is None:
            result = self._collection.insert_one(doc)
            return UserId(value=str(result.inserted_id))
        else:
            self._collection.update_one(
                {"_id": ObjectId(user.id.value)},
                {"$set": doc},
            )
            return user.id

    def find_by_id(self, user_id: UserId) -> User | None:
        """Find a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User if found, None otherwise.
        """
        doc = self._collection.find_one({"_id": ObjectId(user_id.value)})
        if doc is None:
            return None
        return self._to_entity(doc)

    def find_by_email(self, email: str) -> User | None:
        """Find a user by their email address.

        Email lookup is case-insensitive.

        Args:
            email: The email address to search for.

        Returns:
            The User if found, None otherwise.
        """
        doc = self._collection.find_one({"email": email.lower()})
        if doc is None:
            return None
        return self._to_entity(doc)

    def _to_document(self, user: User) -> UserDoc:
        """Map domain entity to MongoDB document.

        Args:
            user: The user entity to convert.

        Returns:
            Dictionary suitable for MongoDB insertion/update.
        """
        return {
            "email": user.email,
            "display_name": user.display_name,
            "password_hash": user.password_hash,
            "activated_at": user.activated_at.isoformat()
            if user.activated_at
            else None,
        }

    def _to_entity(self, doc: UserDoc) -> User:
        """Map MongoDB document to domain entity.

        Args:
            doc: MongoDB document to convert.

        Returns:
            User entity with data from the document.
        """
        activated_at_str = doc.get("activated_at")
        activated_at = (
            datetime.fromisoformat(activated_at_str) if activated_at_str else None
        )

        return User(
            id=UserId(value=str(doc["_id"])),
            email=doc["email"],
            display_name=doc.get("display_name", ""),
            password_hash=doc.get("password_hash"),
            activated_at=activated_at,
        )


def get_users_collection() -> Collection:
    """Get MongoDB users collection, initializing connection if needed."""
    return get_database().users
