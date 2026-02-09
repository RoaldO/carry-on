"""Tests for MongoCourseRepository."""

from typing import Any
from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId
from pymongo.collection import Collection
import pytest

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.repositories.course_repository import CourseRepository
from carry_on.domain.course.value_objects.hole import Hole
from carry_on.infrastructure.repositories.course.mongo_course_repository import (
    MongoCourseRepository,
)


def _make_holes(n: int) -> tuple[Hole, ...]:
    """Helper to create a valid sequence of n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4, 4, 4, 3, 5, 4, 3, 4, 5, 4]
    return tuple(
        Hole(hole_number=i + 1, par=pars[i % len(pars)], stroke_index=i + 1)
        for i in range(n)
    )


@pytest.fixture
def collection() -> Collection[Any]:
    return MagicMock(spec=Collection)


@pytest.fixture
def repo(collection: Collection[Any]) -> MongoCourseRepository:
    return MongoCourseRepository(collection)


@allure.feature("Infrastructure")
@allure.story("MongoDB Course Repository")
class TestCourseRepositoryProtocol:
    """Tests for CourseRepository protocol compliance."""

    def test_mongo_repository_implements_protocol(
        self,
        repo: MongoCourseRepository,
    ) -> None:
        """MongoCourseRepository should implement CourseRepository protocol."""
        assert isinstance(repo, CourseRepository)


@allure.feature("Infrastructure")
@allure.story("MongoDB Course Repository")
class TestMongoCourseRepositorySave:
    """Tests for MongoCourseRepository.save() method."""

    def test_save_returns_course_id(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should return CourseId with inserted document ID."""
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        course = Course.create(name="Test Course", holes=_make_holes(9))
        result = repo.save(course, user_id="user123")

        assert isinstance(result, CourseId)
        assert result.value == str(inserted_id)

    def test_save_creates_correct_document(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should create MongoDB document with correct structure."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        course = Course.create(name="Pitch & Putt", holes=_make_holes(9))
        repo.save(course, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]

        assert doc["name"] == "Pitch & Putt"
        assert doc["user_id"] == "user123"
        assert len(doc["holes"]) == 9
        assert "created_at" in doc

        # Verify hole structure
        first_hole = doc["holes"][0]
        assert first_hole["hole_number"] == 1
        assert first_hole["par"] == 4
        assert first_hole["stroke_index"] == 1

    def test_save_18_hole_course(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should save 18-hole course with all holes."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        course = Course.create(name="Championship", holes=_make_holes(18))
        repo.save(course, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        assert len(doc["holes"]) == 18


@allure.feature("Infrastructure")
@allure.story("MongoDB Course Repository")
class TestMongoCourseRepositoryFindByUser:
    """Tests for MongoCourseRepository.find_by_user() method."""

    def _create_mock_cursor(self, docs: list[dict[str, Any]]) -> MagicMock:
        """Create a mock cursor that returns documents."""
        cursor = MagicMock()
        cursor.__iter__ = Mock(return_value=iter(docs))
        return cursor

    def test_find_by_user_returns_courses(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should return list of Course aggregates for user."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "name": "Test Course",
                "holes": [
                    {"hole_number": i + 1, "par": 4, "stroke_index": i + 1}
                    for i in range(9)
                ],
                "created_at": "2026-01-15T10:00:00+00:00",
                "user_id": "user123",
            }
        ]
        collection.find.return_value = self._create_mock_cursor(docs)

        result = repo.find_by_user("user123")

        assert len(result) == 1
        course = result[0]
        assert isinstance(course, Course)
        assert course.id == CourseId(value=str(doc_id))
        assert course.name == "Test Course"
        assert course.number_of_holes == 9

    def test_find_by_user_queries_correct_user(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should query MongoDB with correct user_id filter."""
        collection.find.return_value = self._create_mock_cursor([])

        repo.find_by_user("user123")

        collection.find.assert_called_once_with({"user_id": "user123"})

    def test_find_by_user_returns_empty_list_when_no_results(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should return empty list when user has no courses."""
        collection.find.return_value = self._create_mock_cursor([])

        result = repo.find_by_user("nonexistent_user")

        assert result == []

    def test_find_by_user_maps_holes_correctly(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Should correctly map hole documents to Hole value objects."""
        doc_id = ObjectId()
        docs = [
            {
                "_id": doc_id,
                "name": "Varied Course",
                "holes": [
                    {"hole_number": 1, "par": 3, "stroke_index": 5},
                    {"hole_number": 2, "par": 5, "stroke_index": 1},
                    {"hole_number": 3, "par": 4, "stroke_index": 3},
                    {"hole_number": 4, "par": 4, "stroke_index": 7},
                    {"hole_number": 5, "par": 3, "stroke_index": 9},
                    {"hole_number": 6, "par": 4, "stroke_index": 2},
                    {"hole_number": 7, "par": 5, "stroke_index": 4},
                    {"hole_number": 8, "par": 4, "stroke_index": 6},
                    {"hole_number": 9, "par": 4, "stroke_index": 8},
                ],
                "created_at": "2026-01-15T10:00:00",
                "user_id": "user123",
            }
        ]
        collection.find.return_value = self._create_mock_cursor(docs)

        result = repo.find_by_user("user123")

        course = result[0]
        assert course.holes[0] == Hole(hole_number=1, par=3, stroke_index=5)
        assert course.holes[1] == Hole(hole_number=2, par=5, stroke_index=1)


@allure.feature("Infrastructure")
@allure.story("MongoDB Course Repository")
class TestMongoCourseRepositoryMapping:
    """Tests for document-to-entity and entity-to-document mapping."""

    def test_roundtrip_course(
        self,
        collection: Collection[Any],
        repo: MongoCourseRepository,
    ) -> None:
        """Mapping should preserve all data through save/load cycle."""
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        original = Course.create(name="Roundtrip Course", holes=_make_holes(9))
        repo.save(original, user_id="user123")

        doc = collection.insert_one.call_args[0][0]
        doc["_id"] = inserted_id

        cursor = MagicMock()
        cursor.__iter__ = Mock(return_value=iter([doc]))
        collection.find.return_value = cursor

        retrieved = repo.find_by_user("user123")[0]

        assert retrieved.name == original.name
        assert retrieved.number_of_holes == original.number_of_holes
        assert retrieved.total_par == original.total_par
        for orig_hole, ret_hole in zip(original.holes, retrieved.holes):
            assert orig_hole == ret_hole
