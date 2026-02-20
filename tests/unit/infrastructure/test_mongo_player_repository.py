"""Tests for MongoPlayerRepository."""

from decimal import Decimal
from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId
from pymongo.collection import Collection
import pytest

from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.repositories.player_repository import PlayerRepository
from carry_on.domain.player.value_objects.handicap import Handicap
from carry_on.infrastructure.repositories.player.mongo_player_repository import (
    MongoPlayerRepository,
)


@pytest.fixture
def collection() -> Collection[Player]:
    return MagicMock(spec=Collection)


@pytest.fixture
def repo(collection: Collection[Player]) -> PlayerRepository:
    return MongoPlayerRepository(collection)


@allure.feature("Infrastructure")
@allure.story("MongoDB Player Repository")
class TestPlayerRepositoryProtocol:
    """Tests for PlayerRepository protocol compliance."""

    def test_mongo_repository_implements_protocol(
        self,
        repo: PlayerRepository,
    ) -> None:
        """MongoPlayerRepository should implement PlayerRepository protocol."""
        assert isinstance(repo, PlayerRepository)


@allure.feature("Infrastructure")
@allure.story("MongoDB Player Repository")
class TestMongoPlayerRepositorySave:
    """Tests for MongoPlayerRepository.save() method."""

    def test_save_player_returns_player_id(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should return PlayerId from upserted document."""
        upserted_id = ObjectId()
        collection.update_one.return_value = Mock(
            upserted_id=upserted_id, matched_count=0
        )

        player = Player(
            id=None,
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )

        result = repo.save(player)

        assert isinstance(result, PlayerId)
        assert result.value == str(upserted_id)

    def test_save_player_uses_upsert(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should call update_one with upsert=True."""
        collection.update_one.return_value = Mock(
            upserted_id=ObjectId(), matched_count=0
        )

        player = Player(
            id=None,
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )

        repo.save(player)

        collection.update_one.assert_called_once()
        call_kwargs = collection.update_one.call_args
        assert call_kwargs.kwargs.get("upsert") is True or (
            len(call_kwargs.args) > 2 and call_kwargs.args[2] is True
        )

    def test_save_player_filters_by_user_id(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should filter on user_id for the upsert."""
        collection.update_one.return_value = Mock(
            upserted_id=ObjectId(), matched_count=0
        )

        player = Player(
            id=None,
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )

        repo.save(player)

        filter_arg = collection.update_one.call_args.args[0]
        assert filter_arg == {"user_id": "user123"}

    def test_save_player_stores_handicap_as_string(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should store handicap value as string in MongoDB document."""
        collection.update_one.return_value = Mock(
            upserted_id=ObjectId(), matched_count=0
        )

        player = Player(
            id=None,
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )

        repo.save(player)

        update_arg = collection.update_one.call_args.args[1]
        doc = update_arg["$set"]
        assert doc["handicap"] == "14.3"

    def test_save_player_with_null_handicap(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should store None handicap as None in MongoDB."""
        collection.update_one.return_value = Mock(
            upserted_id=ObjectId(), matched_count=0
        )

        player = Player(id=None, user_id="user123", handicap=None)

        repo.save(player)

        update_arg = collection.update_one.call_args.args[1]
        doc = update_arg["$set"]
        assert doc["handicap"] is None

    def test_save_existing_player_returns_existing_id(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should return existing PlayerId when matched (not upserted)."""
        existing_id = ObjectId()
        collection.update_one.return_value = Mock(upserted_id=None, matched_count=1)
        collection.find_one.return_value = {
            "_id": existing_id,
            "user_id": "user123",
            "handicap": "14.3",
        }

        player = Player(
            id=None,
            user_id="user123",
            handicap=Handicap(value=Decimal("18.0")),
        )

        result = repo.save(player)

        assert isinstance(result, PlayerId)
        assert result.value == str(existing_id)


@allure.feature("Infrastructure")
@allure.story("MongoDB Player Repository")
class TestMongoPlayerRepositoryFindByUserId:
    """Tests for MongoPlayerRepository.find_by_user_id() method."""

    def test_find_by_user_id_returns_player(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should return Player entity when document exists."""
        doc_id = ObjectId()
        collection.find_one.return_value = {
            "_id": doc_id,
            "user_id": "user123",
            "handicap": "14.3",
        }

        result = repo.find_by_user_id("user123")

        assert result is not None
        assert isinstance(result, Player)
        assert result.id == PlayerId(value=str(doc_id))
        assert result.user_id == "user123"
        assert result.handicap == Handicap(value=Decimal("14.3"))

    def test_find_by_user_id_returns_none_when_not_found(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should return None when no player document exists."""
        collection.find_one.return_value = None

        result = repo.find_by_user_id("nonexistent")

        assert result is None

    def test_find_by_user_id_queries_correct_user(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should query MongoDB with correct user_id filter."""
        collection.find_one.return_value = None

        repo.find_by_user_id("user123")

        collection.find_one.assert_called_once_with({"user_id": "user123"})

    def test_find_by_user_id_with_null_handicap(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Should return Player with None handicap when stored as null."""
        doc_id = ObjectId()
        collection.find_one.return_value = {
            "_id": doc_id,
            "user_id": "user123",
            "handicap": None,
        }

        result = repo.find_by_user_id("user123")

        assert result is not None
        assert result.handicap is None


@allure.feature("Infrastructure")
@allure.story("MongoDB Player Repository")
class TestMongoPlayerRepositoryRoundtrip:
    """Tests for document-to-entity and entity-to-document mapping."""

    def test_roundtrip_player_with_handicap(
        self,
        collection: Collection[Player],
        repo: PlayerRepository,
    ) -> None:
        """Mapping should preserve all data for player with handicap."""
        upserted_id = ObjectId()
        collection.update_one.return_value = Mock(
            upserted_id=upserted_id, matched_count=0
        )

        original = Player(
            id=None,
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )

        repo.save(original)

        # Get the document that was saved
        update_arg = collection.update_one.call_args.args[1]
        doc = update_arg["$set"]
        doc["_id"] = upserted_id

        # Mock find to return our document
        collection.find_one.return_value = doc

        retrieved = repo.find_by_user_id("user123")

        assert retrieved is not None
        assert retrieved.user_id == original.user_id
        assert retrieved.handicap == original.handicap
