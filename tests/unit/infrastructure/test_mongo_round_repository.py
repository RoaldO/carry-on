"""Tests for MongoRoundRepository."""

import datetime
from typing import Any
from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId
from pymongo.collection import Collection

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository
from carry_on.domain.course.value_objects.hole_result import HoleResult
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
            course="Pitch & Putt",
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
            course="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
        )
        round.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1))
        round.record_hole(HoleResult(hole_number=2, strokes=3, par=3, stroke_index=2))

        repo.save(round, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]

        assert doc["course"] == "Pitch & Putt"
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
                "course": "Pitch & Putt",
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
        assert round.course == "Pitch & Putt"

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
                "course": "Test Course",
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
