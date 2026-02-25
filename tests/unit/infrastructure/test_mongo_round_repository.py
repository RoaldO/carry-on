"""Tests for MongoRoundRepository."""

import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId
from pymongo.collection import Collection

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.round_status import RoundStatus
from carry_on.domain.course.value_objects.stableford_score import StablefordScore
from carry_on.infrastructure.repositories.course.mongo_round_repository import (
    MongoRoundRepository,
)

import pytest


@pytest.fixture
def collection() -> Collection[Any]:
    return MagicMock(spec=Collection)


@pytest.fixture
def repo(collection: Collection[Any]) -> MongoRoundRepository:
    return MongoRoundRepository(collection)


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository")
class TestRoundRepositoryProtocol:
    """Tests for RoundRepository protocol compliance."""

    def test_mongo_repository_implements_protocol(
        self,
        repo: MongoRoundRepository,
    ) -> None:
        """MongoRoundRepository should implement RoundRepository protocol."""
        assert isinstance(repo, RoundRepository)


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository")
class TestMongoRoundRepositorySave:
    """Tests for MongoRoundRepository.save() method."""

    def test_save_returns_round_id(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should return RoundId with inserted document ID."""
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        result = repo.save(round, user_id="user123")

        assert isinstance(result, RoundId)
        assert result.value == str(inserted_id)

    def test_save_creates_document_with_correct_fields(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should create MongoDB document with correct structure."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        round.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1))
        round.record_hole(HoleResult(hole_number=2, strokes=3, par=3, stroke_index=2))

        repo.save(round, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]

        assert doc["course_name"] == "Pitch & Putt"
        assert doc["date"] == "2026-02-01"
        assert doc["user_id"] == "user123"
        assert "created_at" in doc
        assert len(doc["holes"]) == 2
        assert doc["holes"][0]["hole_number"] == 1
        assert doc["holes"][0]["strokes"] == 4
        assert doc["holes"][0]["par"] == 4
        assert doc["holes"][0]["stroke_index"] == 1


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository")
class TestMongoRoundRepositoryFindByUser:
    """Tests for MongoRoundRepository.find_by_user() method."""

    def _create_mock_cursor(self, docs: list[dict[str, Any]]) -> MagicMock:
        """Create a mock cursor that returns documents."""
        cursor = MagicMock()
        cursor.__iter__ = Mock(return_value=iter(docs))
        return cursor

    def test_find_by_user_returns_rounds(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should return list of Round aggregates for user."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": [
                    {
                        "hole_number": 1,
                        "strokes": 4,
                        "par": 4,
                        "stroke_index": 1,
                    },
                ],
                "created_at": "2026-02-01T10:00:00+00:00",
                "user_id": "user123",
            }
        ]
        collection.find.return_value = self._create_mock_cursor(docs)

        result = repo.find_by_user("user123")

        assert len(result) == 1
        round = result[0]
        assert isinstance(round, Round)
        assert round.id == RoundId(value=str(doc_id))
        assert round.course_name == "Pitch & Putt"

    def test_find_by_user_returns_empty_list(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should return empty list when user has no rounds."""
        collection.find.return_value = self._create_mock_cursor([])

        result = repo.find_by_user("nonexistent_user")

        assert result == []

    def test_find_by_user_maps_holes_correctly(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should correctly map hole result documents to HoleResult value objects."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "course_name": "Test Course",
                "date": "2026-02-01",
                "holes": [
                    {
                        "hole_number": 1,
                        "strokes": 5,
                        "par": 4,
                        "stroke_index": 3,
                    },
                    {
                        "hole_number": 2,
                        "strokes": 3,
                        "par": 3,
                        "stroke_index": 7,
                    },
                ],
                "created_at": "2026-02-01T10:00:00+00:00",
                "user_id": "user123",
            }
        ]
        collection.find.return_value = self._create_mock_cursor(docs)

        result = repo.find_by_user("user123")

        round = result[0]
        assert len(round.holes) == 2
        assert round.holes[0] == HoleResult(
            hole_number=1, strokes=5, par=4, stroke_index=3
        )
        assert round.holes[1] == HoleResult(
            hole_number=2, strokes=3, par=3, stroke_index=7
        )


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository")
class TestMongoRoundRepositoryInsertUpdate:
    """Tests for MongoRoundRepository insert/update pattern."""

    def test_save_inserts_new_round_when_id_is_none(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should insert a new round when round.id is None."""
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        round.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1))

        result = repo.save(round, user_id="user123")

        collection.insert_one.assert_called_once()
        collection.update_one.assert_not_called()
        assert result.value == str(inserted_id)

    def test_save_updates_existing_round_when_id_provided(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should update existing round when round.id is provided."""
        round_id = RoundId(value=str(ObjectId()))
        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        round.record_hole(HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1))

        result = repo.save(round, user_id="user123")

        collection.update_one.assert_called_once()
        collection.insert_one.assert_not_called()

        # Verify the filter and update
        call_args = collection.update_one.call_args[0]
        assert call_args[0] == {"_id": ObjectId(round_id.value), "user_id": "user123"}
        assert "$set" in call_args[1]
        assert result == round_id


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository")
class TestMongoRoundRepositoryFindById:
    """Tests for MongoRoundRepository.find_by_id() method."""

    def test_find_by_id_returns_round_with_holes(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should return round with all hole results."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Pitch & Putt",
            "date": "2026-02-01",
            "holes": [
                {
                    "hole_number": 1,
                    "strokes": 4,
                    "par": 4,
                    "stroke_index": 1,
                },
                {
                    "hole_number": 2,
                    "strokes": 3,
                    "par": 3,
                    "stroke_index": 2,
                },
            ],
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.id == RoundId(value=str(doc_id))
        assert result.course_name == "Pitch & Putt"
        assert len(result.holes) == 2
        assert result.holes[0].hole_number == 1
        assert result.holes[1].hole_number == 2

    def test_find_by_id_returns_none_when_not_found(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should return None when round doesn't exist."""
        collection.find_one.return_value = None

        result = repo.find_by_id(RoundId(value=str(ObjectId())), user_id="user123")

        assert result is None

    def test_find_by_id_returns_none_for_different_user(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should return None when round exists but belongs to different user."""
        doc_id = ObjectId()
        collection.find_one.return_value = None  # Simulates filtering by user_id

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="different_user")

        assert result is None
        # Verify the filter includes user_id for security
        call_args = collection.find_one.call_args[0]
        assert call_args[0]["user_id"] == "different_user"


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Status")
class TestMongoRoundRepositoryStatus:
    """Tests for Round status field persistence."""

    def test_save_serializes_status_field(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize status field to short string value."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            status=RoundStatus.FINISHED,
        )

        repo.save(round, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]
        assert doc["status"] == "f"

    def test_save_serializes_default_status(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize default IN_PROGRESS status."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )

        repo.save(round, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]
        assert doc["status"] == "ip"

    def test_find_deserializes_status_field(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize status field from string value."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Test Course",
            "date": "2026-02-01",
            "holes": [],
            "status": "f",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.status == RoundStatus.FINISHED

    def test_find_defaults_to_in_progress_when_status_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should default to IN_PROGRESS for old documents without status field."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Test Course",
            "date": "2026-02-01",
            "holes": [],
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
            # No status field - simulates old document
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.status == RoundStatus.IN_PROGRESS

    def test_status_persists_across_save_load_cycle(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should preserve status through save and load operations."""
        doc_id = ObjectId()

        # Save with ABORTED status
        collection.insert_one.return_value = Mock(inserted_id=doc_id)
        round = Round.create(
            course_name="Test Course",
            date=datetime.date(2026, 2, 1),
            status=RoundStatus.ABORTED,
        )
        repo.save(round, user_id="user123")

        # Extract saved document
        saved_doc = collection.insert_one.call_args[0][0]

        # Load it back
        load_doc = {
            "_id": doc_id,
            **saved_doc,
        }
        collection.find_one.return_value = load_doc
        loaded_round = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert loaded_round is not None
        assert loaded_round.status == RoundStatus.ABORTED

    def _create_mock_cursor(self, docs: list[dict[str, Any]]) -> MagicMock:
        """Create a mock cursor that returns documents."""
        cursor = MagicMock()
        cursor.__iter__ = Mock(return_value=iter(docs))
        return cursor

    def test_find_by_user_deserializes_all_statuses(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should correctly deserialize all three status values."""
        docs = [
            {
                "_id": ObjectId(),
                "course_name": "Course 1",
                "date": "2026-02-01",
                "holes": [],
                "status": "ip",
                "created_at": "2026-02-01T10:00:00+00:00",
                "user_id": "user123",
            },
            {
                "_id": ObjectId(),
                "course_name": "Course 2",
                "date": "2026-02-02",
                "holes": [],
                "status": "f",
                "created_at": "2026-02-02T10:00:00+00:00",
                "user_id": "user123",
            },
            {
                "_id": ObjectId(),
                "course_name": "Course 3",
                "date": "2026-02-03",
                "holes": [],
                "status": "a",
                "created_at": "2026-02-03T10:00:00+00:00",
                "user_id": "user123",
            },
        ]
        collection.find.return_value = self._create_mock_cursor(docs)

        results = repo.find_by_user("user123")

        assert len(results) == 3
        assert results[0].status == RoundStatus.IN_PROGRESS
        assert results[1].status == RoundStatus.FINISHED
        assert results[2].status == RoundStatus.ABORTED


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Player Handicap")
class TestMongoRoundRepositoryPlayerHandicap:
    """Tests for player_handicap field persistence."""

    def test_save_serializes_player_handicap(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize Decimal handicap as string."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            player_handicap=Decimal("18.4"),
        )

        repo.save(round, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["player_handicap"] == "18.4"

    def test_save_serializes_none_handicap(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None handicap as None."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            player_handicap=None,
        )

        repo.save(round, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["player_handicap"] is None

    def test_find_deserializes_player_handicap(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize string handicap back to Decimal."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Pitch & Putt",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "player_handicap": "18.4",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.player_handicap == Decimal("18.4")

    def test_find_defaults_to_none_when_handicap_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should default to None for old documents without player_handicap."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Pitch & Putt",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
            # No player_handicap field - simulates old document
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.player_handicap is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Stableford Score")
class TestMongoRoundRepositoryStablefordScore:
    """Tests for stableford_score field persistence."""

    def test_save_serializes_stableford_score(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize StablefordScore as integer."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        round_.stableford_score = StablefordScore(points=36)

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["stableford_score"] == 36

    def test_save_serializes_none_stableford_score(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None score as None."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        # stableford_score defaults to None

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["stableford_score"] is None

    def test_find_deserializes_stableford_score(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize integer back to StablefordScore."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Pitch & Putt",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "stableford_score": 36,
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.stableford_score == StablefordScore(points=36)

    def test_find_deserializes_none_stableford_score(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize None score."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Pitch & Putt",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "stableford_score": None,
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.stableford_score is None

    def test_find_defaults_to_none_when_stableford_score_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should default to None for old docs without stableford_score."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Pitch & Putt",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
            # No stableford_score field - old document
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.stableford_score is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Slope & Course Rating")
class TestMongoRoundRepositoryRatings:
    """Tests for slope_rating and course_rating field persistence."""

    def test_save_serializes_ratings_as_strings(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize Decimal ratings as strings."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Hilly Links",
            date=datetime.date(2026, 2, 1),
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
        )
        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["slope_rating"] == "125"
        assert doc["course_rating"] == "72.3"

    def test_save_serializes_none_ratings(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None ratings as None."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Old Course",
            date=datetime.date(2026, 2, 1),
        )
        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["slope_rating"] is None
        assert doc["course_rating"] is None

    def test_find_deserializes_ratings_to_decimal(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize string ratings back to Decimal."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Hilly Links",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "slope_rating": "125",
            "course_rating": "72.3",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.slope_rating == Decimal("125")
        assert result.course_rating == Decimal("72.3")

    def test_find_defaults_to_none_when_ratings_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Old documents without ratings should default to None."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Legacy Course",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "created_at": "2025-06-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.slope_rating is None
        assert result.course_rating is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Course Handicap")
class TestMongoRoundRepositoryCourseHandicap:
    """Tests for course_handicap field persistence."""

    def test_save_serializes_course_handicap(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize integer course_handicap."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Hilly Links",
            date=datetime.date(2026, 2, 1),
        )
        round_.course_handicap = 21

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["course_handicap"] == 21

    def test_save_serializes_none_course_handicap(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None course_handicap as None."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        # course_handicap defaults to None

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["course_handicap"] is None

    def test_find_deserializes_course_handicap(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize integer course_handicap."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Hilly Links",
            "date": "2026-02-01",
            "holes": [],
            "status": "f",
            "course_handicap": 21,
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.course_handicap == 21

    def test_find_defaults_to_none_when_course_handicap_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Old documents without course_handicap should default to None."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Legacy Course",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "created_at": "2025-06-01T10:00:00+00:00",
            "user_id": "user123",
            # No course_handicap field - old document
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.course_handicap is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Num Holes & Course Par")
class TestMongoRoundRepositoryNumHolesCoursePar:
    """Tests for num_holes and course_par field persistence."""

    def test_save_serializes_num_holes_and_course_par(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize num_holes and course_par as integers."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Hilly Links",
            date=datetime.date(2026, 2, 1),
            num_holes=18,
            course_par=72,
        )
        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["num_holes"] == 18
        assert doc["course_par"] == 72

    def test_save_serializes_none_num_holes_and_course_par(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None values as None."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Old Course",
            date=datetime.date(2026, 2, 1),
        )
        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["num_holes"] is None
        assert doc["course_par"] is None

    def test_find_deserializes_num_holes_and_course_par(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize num_holes and course_par from document."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Hilly Links",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "num_holes": 18,
            "course_par": 72,
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.num_holes == 18
        assert result.course_par == 72

    def test_find_defaults_to_none_when_fields_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Old documents without num_holes/course_par should default to None."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Legacy Course",
            "date": "2026-02-01",
            "holes": [],
            "status": "ip",
            "created_at": "2025-06-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.num_holes is None
        assert result.course_par is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Per-Hole Stableford Points")
class TestMongoRoundRepositoryHoleStablefordPoints:
    """Tests for stableford_points per hole in MongoDB persistence."""

    def test_save_serializes_hole_stableford_points(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize stableford_points on each hole document."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Hilly Links",
            date=datetime.date(2026, 2, 1),
            player_handicap=Decimal("18"),
            num_holes=18,
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1))

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert "stableford_points" in doc["holes"][0]
        assert doc["holes"][0]["stableford_points"] == 2

    def test_save_serializes_none_stableford_points(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None stableford_points for holes without it."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Old Course",
            date=datetime.date(2026, 2, 1),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1))

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["holes"][0]["stableford_points"] is None

    def test_find_deserializes_hole_stableford_points(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize stableford_points from hole document."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Hilly Links",
            "date": "2026-02-01",
            "holes": [
                {
                    "hole_number": 1,
                    "strokes": 5,
                    "par": 4,
                    "stroke_index": 1,
                    "stableford_points": 2,
                },
            ],
            "status": "ip",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.holes[0].stableford_points == 2

    def test_find_defaults_to_none_when_stableford_points_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Old docs without stableford_points per hole should default to None."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Legacy Course",
            "date": "2026-02-01",
            "holes": [
                {
                    "hole_number": 1,
                    "strokes": 4,
                    "par": 4,
                    "stroke_index": 1,
                    # No stableford_points — old document
                },
            ],
            "status": "ip",
            "created_at": "2025-06-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.holes[0].stableford_points is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Round Repository - Per-Hole Handicap Strokes")
class TestMongoRoundRepositoryHoleHandicapStrokes:
    """Tests for handicap_strokes per hole in MongoDB persistence."""

    def test_save_serializes_hole_handicap_strokes(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize handicap_strokes on each hole document."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Hilly Links",
            date=datetime.date(2026, 2, 1),
            player_handicap=Decimal("20"),
            num_holes=18,
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1))

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert "handicap_strokes" in doc["holes"][0]
        # CH=20 → SI 1 gets 2 strokes
        assert doc["holes"][0]["handicap_strokes"] == 2

    def test_save_serializes_none_handicap_strokes(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should serialize None handicap_strokes for holes without it."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        round_ = Round.create(
            course_name="Old Course",
            date=datetime.date(2026, 2, 1),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1))

        repo.save(round_, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert doc["holes"][0]["handicap_strokes"] is None

    def test_find_deserializes_hole_handicap_strokes(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Should deserialize handicap_strokes from hole document."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Hilly Links",
            "date": "2026-02-01",
            "holes": [
                {
                    "hole_number": 1,
                    "strokes": 5,
                    "par": 4,
                    "stroke_index": 1,
                    "handicap_strokes": 2,
                },
            ],
            "status": "ip",
            "created_at": "2026-02-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.holes[0].handicap_strokes == 2

    def test_find_defaults_to_none_when_handicap_strokes_missing(
        self,
        collection: Collection[Any],
        repo: MongoRoundRepository,
    ) -> None:
        """Old docs without handicap_strokes per hole should default to None."""
        doc_id = ObjectId()
        doc = {
            "_id": doc_id,
            "course_name": "Legacy Course",
            "date": "2026-02-01",
            "holes": [
                {
                    "hole_number": 1,
                    "strokes": 4,
                    "par": 4,
                    "stroke_index": 1,
                    # No handicap_strokes — old document
                },
            ],
            "status": "ip",
            "created_at": "2025-06-01T10:00:00+00:00",
            "user_id": "user123",
        }
        collection.find_one.return_value = doc

        result = repo.find_by_id(RoundId(value=str(doc_id)), user_id="user123")

        assert result is not None
        assert result.holes[0].handicap_strokes is None
