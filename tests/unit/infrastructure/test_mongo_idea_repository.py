from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId
from pymongo.collection import Collection
import pytest

from carry_on.domain.entities.idea import Idea, IdeaId
from carry_on.domain.repositories.idea_repository import IdeaRepository
from carry_on.infrastructure.repositories.mongo_idea_repository import (
    MongoIdeaRepository,
)


@pytest.fixture
def collection() -> Collection[Idea]:
    return MagicMock(spec=Collection)


@pytest.fixture
def repo(collection: Collection[Idea]) -> IdeaRepository:
    return MongoIdeaRepository(collection)


@allure.feature("Infrastructure")
@allure.story("MongoDB Idea Repository")
class TestIdeaRepositoryProtocol:
    """Tests for IdeaRepository protocol compliance."""

    def test_mongo_repository_implements_protocol(
        self,
        repo: IdeaRepository,
    ) -> None:
        """MongoIdeaRepository should implement IdeaRepository protocol."""
        assert isinstance(repo, IdeaRepository)


@allure.feature("Infrastructure")
@allure.story("MongoDB Idea Repository")
class TestMongoIdeaRepositorySave:
    """Tests for MongoIdeaRepository.save() method."""

    def test_save_idea_returns_idea_id(
        self,
        collection: Collection[Idea],
        repo: IdeaRepository,
    ) -> None:
        """Should return IdeaId with inserted document ID."""
        inserted_id = ObjectId()
        collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        stroke = Idea.create_idea(
            description="Use AsyncIO for better concurrency",
        )

        result = repo.save(stroke, user_id="user123")

        assert isinstance(result, IdeaId)
        assert result.value == str(inserted_id)

    def test_save_idea_creates_correct_document(
        self,
        collection: Collection[Idea],
        repo: IdeaRepository,
    ) -> None:
        """Should create MongoDB document with correct structure."""
        collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        idea = Idea.create_idea(
            description="Use AsyncIO for better concurrency",
        )

        repo.save(idea, user_id="user123")

        collection.insert_one.assert_called_once()
        doc = collection.insert_one.call_args[0][0]

        assert doc["description"] == "Use AsyncIO for better concurrency"
        assert "created_at" in doc
