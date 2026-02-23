"""MongoDB implementation of RoundRepository."""

import datetime
from decimal import Decimal
from typing import NotRequired, TypedDict

from bson.objectid import ObjectId
from pymongo.collection import Collection

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.round_status import RoundStatus
from carry_on.domain.course.value_objects.stableford_score import StablefordScore


class HoleResultDoc(TypedDict):
    hole_number: int
    strokes: int
    par: int
    stroke_index: int


class RoundDoc(TypedDict):
    _id: NotRequired[ObjectId]
    course_name: str
    date: str
    holes: list[HoleResultDoc]
    status: NotRequired[str]  # For backward compatibility with old documents
    player_handicap: NotRequired[str | None]
    stableford_score: NotRequired[int | None]
    created_at: str
    user_id: str


class MongoRoundRepository:
    """MongoDB implementation of the RoundRepository protocol.

    Maps domain aggregates to/from MongoDB documents and handles
    persistence operations.
    """

    def __init__(self, collection: Collection[RoundDoc]) -> None:
        """Initialize repository with MongoDB collection.

        Args:
            collection: The MongoDB collection for storing rounds.
        """
        self._collection = collection

    def save(self, round: Round, user_id: str) -> RoundId:
        """Save a round (insert if new, update if existing).

        Args:
            round: The round aggregate to save.
            user_id: The ID of the user who owns this round.

        Returns:
            The RoundId of the saved round.
        """
        doc = self._to_document(round, user_id)

        if round.id is None:
            # Insert new round
            result = self._collection.insert_one(doc)
            return RoundId(value=str(result.inserted_id))
        else:
            # Update existing round
            self._collection.update_one(
                {"_id": ObjectId(round.id.value), "user_id": user_id},
                {"$set": doc},
            )
            return round.id

    def find_by_user(self, user_id: str) -> list[Round]:
        """Find rounds for a user.

        Args:
            user_id: The ID of the user whose rounds to find.

        Returns:
            List of Round aggregates owned by the user, newest first.
        """
        cursor = self._collection.find({"user_id": user_id})
        return [self._to_entity(doc) for doc in cursor]

    def find_by_id(self, round_id: RoundId, user_id: str) -> Round | None:
        """Find a round by ID for a specific user.

        Args:
            round_id: The ID of the round to find.
            user_id: The ID of the user who owns the round.

        Returns:
            The Round aggregate if found, None otherwise.
        """
        doc = self._collection.find_one(
            {"_id": ObjectId(round_id.value), "user_id": user_id}
        )
        if doc is None:
            return None
        return self._to_entity(doc)

    def _to_document(self, round: Round, user_id: str) -> RoundDoc:
        """Map domain aggregate to MongoDB document."""
        return {
            "course_name": round.course_name,
            "date": round.date.isoformat(),
            "holes": [
                {
                    "hole_number": h.hole_number,
                    "strokes": h.strokes,
                    "par": h.par,
                    "stroke_index": h.stroke_index,
                }
                for h in round.holes
            ],
            "status": round.status.value,
            "player_handicap": (
                str(round.player_handicap)
                if round.player_handicap is not None
                else None
            ),
            "stableford_score": (
                round.stableford_score.points
                if round.stableford_score is not None
                else None
            ),
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "user_id": user_id,
        }

    def _to_entity(self, doc: RoundDoc) -> Round:
        """Map MongoDB document to domain aggregate."""
        raw_handicap = doc.get("player_handicap")
        raw_score = doc.get("stableford_score")
        round = Round.create(
            course_name=doc.get("course_name", "Unknown Course"),
            date=datetime.date.fromisoformat(doc["date"]),
            id=RoundId(value=str(doc["_id"])),
            status=RoundStatus(
                doc.get("status", "ip")
            ),  # Default to IN_PROGRESS for old docs
            player_handicap=(
                Decimal(raw_handicap) if raw_handicap is not None else None
            ),
            stableford_score=(
                StablefordScore(points=raw_score) if raw_score is not None else None
            ),
            created_at=(
                datetime.datetime.fromisoformat(doc["created_at"])
                if "created_at" in doc
                else None
            ),
        )
        for h in doc["holes"]:
            round.record_hole(
                HoleResult(
                    hole_number=h["hole_number"],
                    strokes=h["strokes"],
                    par=h["par"],
                    stroke_index=h["stroke_index"],
                )
            )
        return round
