"""Idea entity representing an idea for the application."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdeaId:
    """Unique identifier for a Idea entity.

    Immutable value object wrapping the database ID.
    """

    value: str


@dataclass
class Idea:
    """Application idea with business rules.

    Business rules:
    - The idea must have a description

    Attributes:
        id: Unique identifier (None for unsaved ideas).
        description: Text description of the idea.
        created_at: Timestamp when the idea was created (None for new ideas).
    """

    id: IdeaId | None
    description: str
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate and enforce business rules."""
        self._validate()

    def _validate(self) -> None:
        """Enforce idea business rules.

        Rules:
        - The idea must have a description
        """
        if not self.description:
            raise ValueError("Description required for Ideas")

    @classmethod
    def create_idea(
        cls,
        description: str,
        id: IdeaId | None = None,
        created_at: datetime | None = None,
    ) -> "Idea":
        """Factory method for creating ideas.

        Args:
            description: Text description of the idea.
            id: Optional identifier (None for new ideas).
            created_at: Optional timestamp when the idea was created.

        Returns:
            A new Idea instance.
        """
        return cls(
            id=id,
            description=description,
            created_at=created_at,
        )
