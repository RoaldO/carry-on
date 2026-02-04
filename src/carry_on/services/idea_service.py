"""IdeaService application service for idea operations."""

from carry_on.domain.entities.idea import Idea, IdeaId
from carry_on.domain.repositories.idea_repository import IdeaRepository
from carry_on.infrastructure.repositories.mongo_idea_repository import (
    MongoIdeaRepository,
    get_ideas_collection,
)


class IdeaService:
    """Application service for idea operations.

    Orchestrates idea creation and retrieval, delegating
    persistence to the repository.
    """

    def __init__(self, repository: IdeaRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The idea repository for persistence operations.
        """
        self._repository = repository

    def record_idea(
        self,
        user_id: str,
        description: str,
    ) -> IdeaId:
        """Record a new idea.

        Args:
            user_id: The user recording the idea.
            description: Description of the idea.

        Returns:
            The ID of the saved idea.

        Raises:
            ValueError: If description missing
        """

        if not description:
            raise ValueError("Description is required")

        idea = Idea.create_idea(
            description=description,
        )

        return self._repository.save(idea, user_id)


def get_ideas_service() -> IdeaService:
    """Get StrokeService with MongoDB repository."""
    collection = get_ideas_collection()
    repository = MongoIdeaRepository(collection)
    return IdeaService(repository)
