import datetime

from dataclasses import dataclass, field
from typing import Self

from carry_on.domain.course.value_objects.hole_result import HoleResult


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
    holes: list[HoleResult] = field(default_factory=list)
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

    def record_hole(self, hole: HoleResult) -> None:
        """Record a hole result. Rejects duplicates."""
        if any(h.hole_number == hole.hole_number for h in self.holes):
            raise ValueError(f"Hole {hole.hole_number} already recorded")
        self.holes.append(hole)

    @property
    def total_strokes(self) -> int:
        """Sum of strokes across all recorded holes."""
        return sum(h.strokes for h in self.holes)

    @property
    def is_complete(self) -> bool:
        """True when all 18 holes are recorded."""
        return len(self.holes) == 18
