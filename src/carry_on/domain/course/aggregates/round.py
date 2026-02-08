import datetime

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class RoundId:
    """Unique identifier for a Round aggregate.

    Immutable value object wrapping the database ID.
    """

    value: str


@dataclass
class Round:
    id: RoundId | None
    course: str
    date: datetime.date
    created_at: datetime.datetime | None = None

    @classmethod
    def create(
        cls,
        course: str,
        date: datetime.date,
        id: RoundId | None = None,
        created_at: datetime.datetime | None = None,
    ) -> Self:
        return cls(
            id=id,
            course=course,
            date=date,
            created_at=created_at,
        )

    def __post_init__(self) -> None:
        """Validate and enforce business rules."""
        self._validate()

    def _validate(self) -> None:
        if not self.course.strip():
            raise ValueError("Course name required")
