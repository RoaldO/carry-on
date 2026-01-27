"""Tests for MongoStrokeRepository."""

from datetime import date, datetime, timezone
from typing import Any
from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId

from domain.entities.stroke import Stroke, StrokeId
from domain.repositories.stroke_repository import StrokeRepository
from domain.value_objects.club_type import ClubType
from domain.value_objects.distance import Distance
from infrastructure.repositories.mongo_stroke_repository import MongoStrokeRepository


@allure.feature("Infrastructure")
@allure.story("MongoDB Stroke Repository")
class TestStrokeRepositoryProtocol:
    """Tests for StrokeRepository protocol compliance."""

    def test_mongo_repository_implements_protocol(self) -> None:
        """MongoStrokeRepository should implement StrokeRepository protocol."""
        collection = MagicMock()
        repo: StrokeRepository = MongoStrokeRepository(collection)
        assert isinstance(repo, StrokeRepository)


@allure.feature("Infrastructure")
@allure.story("MongoDB Stroke Repository")
class TestMongoStrokeRepositorySave:
    """Tests for MongoStrokeRepository.save() method."""

    def test_save_successful_stroke_returns_stroke_id(self) -> None:
        """Should return StrokeId with inserted document ID."""
        collection = MagicMock()
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)
        repo = MongoStrokeRepository(collection)

        stroke = Stroke.create_successful(
            club=ClubType.IRON_7,
            distance=Distance(meters=150),
            stroke_date=date(2024, 1, 15),
        )

        result = repo.save(stroke, user_id="user123")

        assert isinstance(result, StrokeId)
        assert result.value == str(inserted_id)

    def test_save_successful_stroke_creates_correct_document(self) -> None:
        """Should create MongoDB document with correct structure."""
        collection = MagicMock()
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        repo = MongoStrokeRepository(collection)

        stroke = Stroke.create_successful(
            club=ClubType.IRON_7,
            distance=Distance(meters=150),
            stroke_date=date(2024, 1, 15),
        )

        repo.save(stroke, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]

        assert doc["club"] == "7i"
        assert doc["distance"] == 150
        assert doc["fail"] is False
        assert doc["date"] == "2024-01-15"
        assert doc["user_id"] == "user123"
        assert "created_at" in doc

    def test_save_failed_stroke_has_no_distance(self) -> None:
        """Should save failed stroke with null distance."""
        collection = MagicMock()
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        repo = MongoStrokeRepository(collection)

        stroke = Stroke.create_failed(
            club=ClubType.DRIVER,
            stroke_date=date(2024, 1, 15),
        )

        repo.save(stroke, user_id="user456")

        doc = collection.insert_one.call_args[0][0]
        assert doc["club"] == "d"
        assert doc["distance"] is None
        assert doc["fail"] is True


@allure.feature("Infrastructure")
@allure.story("MongoDB Stroke Repository")
class TestMongoStrokeRepositoryFindByUser:
    """Tests for MongoStrokeRepository.find_by_user() method."""

    def _create_mock_cursor(self, docs: list[dict[str, Any]]) -> MagicMock:
        """Create a mock cursor that returns documents."""
        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__iter__ = Mock(return_value=iter(docs))
        return cursor

    def test_find_by_user_returns_strokes(self) -> None:
        """Should return list of Stroke entities for user."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "club": "7i",
                "distance": 150,
                "fail": False,
                "date": "2024-01-15",
                "user_id": "user123",
                "created_at": "2024-01-15T10:00:00+00:00",
            }
        ]
        collection = MagicMock()
        collection.find.return_value = self._create_mock_cursor(docs)
        repo = MongoStrokeRepository(collection)

        result = repo.find_by_user("user123")

        assert len(result) == 1
        stroke = result[0]
        assert isinstance(stroke, Stroke)
        assert stroke.id == StrokeId(value=str(doc_id))
        assert stroke.club == ClubType.IRON_7
        assert stroke.distance == Distance(meters=150)
        assert stroke.fail is False
        assert stroke.stroke_date == date(2024, 1, 15)
        assert stroke.created_at == datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_find_by_user_queries_correct_user(self) -> None:
        """Should query MongoDB with correct user_id filter."""
        collection = MagicMock()
        collection.find.return_value = self._create_mock_cursor([])
        repo = MongoStrokeRepository(collection)

        repo.find_by_user("user123")

        collection.find.assert_called_once_with({"user_id": "user123"})

    def test_find_by_user_sorts_by_created_at_descending(self) -> None:
        """Should sort results by created_at descending (newest first)."""
        collection = MagicMock()
        cursor = self._create_mock_cursor([])
        collection.find.return_value = cursor
        repo = MongoStrokeRepository(collection)

        repo.find_by_user("user123")

        cursor.sort.assert_called_once_with("created_at", -1)

    def test_find_by_user_respects_limit(self) -> None:
        """Should limit results to specified count."""
        collection = MagicMock()
        cursor = self._create_mock_cursor([])
        collection.find.return_value = cursor
        repo = MongoStrokeRepository(collection)

        repo.find_by_user("user123", limit=10)

        cursor.limit.assert_called_once_with(10)

    def test_find_by_user_default_limit_is_20(self) -> None:
        """Should default to limit of 20."""
        collection = MagicMock()
        cursor = self._create_mock_cursor([])
        collection.find.return_value = cursor
        repo = MongoStrokeRepository(collection)

        repo.find_by_user("user123")

        cursor.limit.assert_called_once_with(20)

    def test_find_by_user_handles_failed_strokes(self) -> None:
        """Should correctly map failed strokes (no distance)."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "club": "d",
                "distance": None,
                "fail": True,
                "date": "2024-01-15",
                "user_id": "user123",
                "created_at": "2024-01-15T10:00:00",
            }
        ]
        collection = MagicMock()
        collection.find.return_value = self._create_mock_cursor(docs)
        repo = MongoStrokeRepository(collection)

        result = repo.find_by_user("user123")

        assert len(result) == 1
        stroke = result[0]
        assert stroke.fail is True
        assert stroke.distance is None

    def test_find_by_user_handles_missing_fail_field(self) -> None:
        """Should default fail to False when not present in document."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "club": "7i",
                "distance": 150,
                "date": "2024-01-15",
                "user_id": "user123",
                "created_at": "2024-01-15T10:00:00",
            }
        ]
        collection = MagicMock()
        collection.find.return_value = self._create_mock_cursor(docs)
        repo = MongoStrokeRepository(collection)

        result = repo.find_by_user("user123")

        assert len(result) == 1
        assert result[0].fail is False

    def test_find_by_user_returns_empty_list_when_no_results(self) -> None:
        """Should return empty list when user has no strokes."""
        collection = MagicMock()
        collection.find.return_value = self._create_mock_cursor([])
        repo = MongoStrokeRepository(collection)

        result = repo.find_by_user("nonexistent_user")

        assert result == []

    def test_find_by_user_handles_missing_created_at(self) -> None:
        """Should handle documents without created_at field."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "club": "7i",
                "distance": 150,
                "fail": False,
                "date": "2024-01-15",
                "user_id": "user123",
                # No created_at field
            }
        ]
        collection = MagicMock()
        collection.find.return_value = self._create_mock_cursor(docs)
        repo = MongoStrokeRepository(collection)

        result = repo.find_by_user("user123")

        assert len(result) == 1
        assert result[0].created_at is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Stroke Repository")
class TestMongoStrokeRepositoryMapping:
    """Tests for document-to-entity and entity-to-document mapping."""

    def test_roundtrip_successful_stroke(self) -> None:
        """Mapping should preserve all data for successful strokes."""
        collection = MagicMock()
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        original = Stroke.create_successful(
            club=ClubType.PITCHING_WEDGE,
            distance=Distance(meters=100),
            stroke_date=date(2024, 6, 15),
        )

        repo = MongoStrokeRepository(collection)
        repo.save(original, user_id="user123")

        doc = collection.insert_one.call_args[0][0]

        # Simulate retrieval (add _id)
        doc["_id"] = inserted_id

        # Mock find to return our document
        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__iter__ = Mock(return_value=iter([doc]))
        collection.find.return_value = cursor

        retrieved = repo.find_by_user("user123")[0]

        assert retrieved.club == original.club
        assert retrieved.distance == original.distance
        assert retrieved.fail == original.fail
        assert retrieved.stroke_date == original.stroke_date
        # created_at is set during save, so it should be present after roundtrip
        assert retrieved.created_at is not None

    def test_roundtrip_failed_stroke(self) -> None:
        """Mapping should preserve all data for failed strokes."""
        collection = MagicMock()
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        original = Stroke.create_failed(
            club=ClubType.DRIVER,
            stroke_date=date(2024, 6, 15),
        )

        repo = MongoStrokeRepository(collection)
        repo.save(original, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        doc["_id"] = inserted_id

        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__iter__ = Mock(return_value=iter([doc]))
        collection.find.return_value = cursor

        retrieved = repo.find_by_user("user123")[0]

        assert retrieved.club == original.club
        assert retrieved.distance is None
        assert retrieved.fail is True
        assert retrieved.stroke_date == original.stroke_date
