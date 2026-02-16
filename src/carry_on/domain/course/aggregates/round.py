import datetime

from dataclasses import dataclass, field
from typing import Self

from carry_on.domain.core.value_objects.identifier import Identifier
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.round_status import RoundStatus


@dataclass(frozen=True, slots=True)
class RoundId(Identifier):
    """Unique identifier for a Round aggregate."""


@dataclass
class Round:
    id: RoundId | None
    course_name: str
    date: datetime.date
    holes: list[HoleResult] = field(default_factory=list)
    status: RoundStatus = RoundStatus.IN_PROGRESS
    created_at: datetime.datetime | None = None

    @classmethod
    def create(
        cls,
        course_name: str,
        date: datetime.date,
        id: RoundId | None = None,
        status: RoundStatus = RoundStatus.IN_PROGRESS,
        created_at: datetime.datetime | None = None,
    ) -> Self:
        return cls(
            id=id,
            course_name=course_name,
            date=date,
            status=status,
            created_at=created_at,
        )

    def __post_init__(self) -> None:
        """Validate and enforce business rules."""
        self._validate()

    def _validate(self) -> None:
        if not self.course_name.strip():
            raise ValueError("Course name required")

    def record_hole(self, hole: HoleResult) -> None:
        """Record a hole result. Rejects duplicates."""
        if any(h.hole_number == hole.hole_number for h in self.holes):
            raise ValueError(f"Hole {hole.hole_number} already recorded")
        self.holes.append(hole)

    def update_hole(self, hole: HoleResult) -> None:
        """Update an existing hole result. Raises ValueError if hole not found."""
        for i, h in enumerate(self.holes):
            if h.hole_number == hole.hole_number:
                self.holes[i] = hole
                return
        raise ValueError(f"Hole {hole.hole_number} not yet recorded")

    @property
    def total_strokes(self) -> int:
        """Sum of strokes across all recorded holes."""
        return sum(h.strokes for h in self.holes)

    @property
    def is_complete(self) -> bool:
        """True when all 18 holes are recorded."""
        return len(self.holes) == 18

    def finish(self) -> None:
        """Mark the round as finished.

        Raises:
            ValueError: If the round is already finished.
        """
        if self.status == RoundStatus.FINISHED:
            raise ValueError("Round is already finished")
        self.status = RoundStatus.FINISHED

    def abort(self) -> None:
        """Mark the round as aborted/cancelled.

        Can be called from any state to invalidate a round.
        """
        self.status = RoundStatus.ABORTED

    def resume(self) -> None:
        """Resume an aborted round.

        Raises:
            ValueError: If the round is not in ABORTED state.
        """
        if self.status != RoundStatus.ABORTED:
            raise ValueError("Can only resume aborted rounds")
        self.status = RoundStatus.IN_PROGRESS
