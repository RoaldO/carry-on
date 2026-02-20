"""MongoDB implementation of the PlayerRepository protocol."""

from decimal import Decimal
from typing import NotRequired, TypedDict

from bson.objectid import ObjectId
from pymongo.collection import Collection

from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.value_objects.handicap import Handicap


class PlayerDoc(TypedDict):
    _id: NotRequired[ObjectId]
    user_id: str
    handicap: str | None


class MongoPlayerRepository:
    """MongoDB implementation of the PlayerRepository protocol.

    Uses upsert semantics since there is exactly one Player per User.
    Handicap is stored as a string to avoid floating-point precision issues.
    """

    def __init__(self, collection: Collection[PlayerDoc]) -> None:
        """Initialize repository with MongoDB collection.

        Args:
            collection: The MongoDB collection for storing players.
        """
        self._collection = collection

    def save(self, player: Player) -> PlayerId:
        """Save a player (upsert) and return its ID.

        Args:
            player: The player entity to save.

        Returns:
            The PlayerId of the saved player.
        """
        doc = self._to_document(player)
        result = self._collection.update_one(
            {"user_id": player.user_id},
            {"$set": doc},
            upsert=True,
        )

        if result.upserted_id is not None:
            return PlayerId(value=str(result.upserted_id))

        # Existing document was updated — look up its _id
        existing = self._collection.find_one({"user_id": player.user_id})
        if existing is None:
            raise RuntimeError(
                f"Player document not found after upsert for user {player.user_id}"
            )
        return PlayerId(value=str(existing["_id"]))

    def find_by_user_id(self, user_id: str) -> Player | None:
        """Find a player by their associated user ID.

        Args:
            user_id: The authentication user's ID.

        Returns:
            The Player if found, None otherwise.
        """
        doc = self._collection.find_one({"user_id": user_id})
        if doc is None:
            return None
        return self._to_entity(doc)

    def _to_document(self, player: Player) -> PlayerDoc:
        """Map domain entity to MongoDB document.

        Args:
            player: The player entity to convert.

        Returns:
            Dictionary suitable for MongoDB upsert.
        """
        return {
            "user_id": player.user_id,
            "handicap": str(player.handicap.value) if player.handicap else None,
        }

    def _to_entity(self, doc: PlayerDoc) -> Player:
        """Map MongoDB document to domain entity.

        Args:
            doc: The MongoDB document to convert.

        Returns:
            A Player domain entity.
        """
        handicap_str = doc.get("handicap")
        handicap = Handicap(value=Decimal(handicap_str)) if handicap_str else None

        return Player(
            id=PlayerId(value=str(doc["_id"])),
            user_id=doc["user_id"],
            handicap=handicap,
        )
