"""IdeaRepository protocol defining the repository interface."""

from typing import Protocol, runtime_checkable

from carry_on.domain.entities.idea import Idea, IdeaId


@runtime_checkable
class IdeaRepository(Protocol):
    """Repository interface for Idea entities.

    Defines the contract for idea persistence operations.
    Implementations handle the actual storage mechanism (MongoDB, etc.).

    Note: user_id is passed as a parameter rather than stored in the entity
    because user ownership is a query/security concern, not part of the
    domain concept of an idea.
    """

    def save(self, idea: Idea, user_id: str) -> IdeaId:
        """Save an idea and return its ID.

        Args:
            idea: The idea entity to save.
            user_id: The ID of the user who owns this idea.

        Returns:
            The IdeaId of the saved idea.
        """
