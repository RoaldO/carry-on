"""Stroke entity representing a golf stroke."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Self

from carry_on.domain.core.value_objects.identifier import Identifier
from carry_on.domain.training.value_objects.club_type import ClubType
from carry_on.domain.training.value_objects.distance import Distance


class StrokeId(Identifier):
    __slots__ = ()


@dataclass
class Stroke:
    """Golf stroke entity with business rules.

    Business rules:
    - Failed strokes have no distance (distance is cleared)
    - Successful strokes require a distance

    Attributes:
        id: Unique identifier (None for unsaved strokes).
        club: Type of golf club used.
        fail: Whether the stroke was a failure.
        stroke_date: Date when the stroke occurred.
        distance: Distance achieved (None for failed strokes).
        created_at: Timestamp when the stroke was created (None for new strokes).
    """

    id: StrokeId | None
    club: ClubType
    fail: bool
    stroke_date: date
    distance: Distance | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate and enforce business rules."""
        self._validate()

    def _validate(self) -> None:
        """Enforce stroke business rules.

        Rules:
        - Failed strokes must have no distance
        - Successful strokes must have a distance
        """
        if self.fail and self.distance is not None:
            # Failed strokes should not have distance - clear it
            object.__setattr__(self, "distance", None)
        elif not self.fail and self.distance is None:
            raise ValueError("Distance required for successful strokes")

    @classmethod
    def create_successful(
        cls,
        club: ClubType,
        distance: Distance,
        stroke_date: date,
        id: StrokeId | None = None,
        created_at: datetime | None = None,
    ) -> Self:
        """Factory method for creating successful strokes.

        Args:
            club: Type of golf club used.
            distance: Distance achieved.
            stroke_date: Date of the stroke.
            id: Optional identifier (None for new strokes).
            created_at: Optional timestamp when the stroke was created.

        Returns:
            A new Stroke instance marked as successful.
        """
        return cls(
            id=id,
            club=club,
            fail=False,
            stroke_date=stroke_date,
            distance=distance,
            created_at=created_at,
        )

    @classmethod
    def create_failed(
        cls,
        club: ClubType,
        stroke_date: date,
        id: StrokeId | None = None,
        created_at: datetime | None = None,
    ) -> "Stroke":
        """Factory method for creating failed strokes.

        Args:
            club: Type of golf club used.
            stroke_date: Date of the stroke.
            id: Optional identifier (None for new strokes).
            created_at: Optional timestamp when the stroke was created.

        Returns:
            A new Stroke instance marked as failed (no distance).
        """
        return cls(
            id=id,
            club=club,
            fail=True,
            stroke_date=stroke_date,
            distance=None,
            created_at=created_at,
        )
