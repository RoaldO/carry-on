import datetime

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Self

from carry_on.domain.core.value_objects.identifier import Identifier
from carry_on.domain.course.scoring.stableford import calculate_stableford
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.round_status import RoundStatus
from carry_on.domain.course.value_objects.stableford_score import StablefordScore


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
    player_handicap: Decimal | None = None
    stableford_score: StablefordScore | None = None
    created_at: datetime.datetime | None = None
    slope_rating: Decimal | None = None
    course_rating: Decimal | None = None

    @classmethod
    def create(
        cls,
        course_name: str,
        date: datetime.date,
        id: RoundId | None = None,
        status: RoundStatus = RoundStatus.IN_PROGRESS,
        player_handicap: Decimal | None = None,
        stableford_score: StablefordScore | None = None,
        created_at: datetime.datetime | None = None,
        slope_rating: Decimal | None = None,
        course_rating: Decimal | None = None,
    ) -> Self:
        return cls(
            id=id,
            course_name=course_name,
            date=date,
            status=status,
            player_handicap=player_handicap,
            stableford_score=stableford_score,
            created_at=created_at,
            slope_rating=slope_rating,
            course_rating=course_rating,
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

    _DEFAULT_HANDICAP: Decimal = Decimal("54")

    def finish(self) -> None:
        """Mark the round as finished and calculate Stableford score.

        Uses the player's handicap to compute the Stableford score.
        When no handicap is stored, defaults to 54 (WHS maximum).

        Raises:
            ValueError: If the round is already finished.
            ValueError: If the round does not have exactly 9 or 18 holes.
        """
        if self.status == RoundStatus.FINISHED:
            raise ValueError("Round is already finished")
        num_holes = len(self.holes)
        if num_holes not in (9, 18):
            raise ValueError("Round must have either 9 or 18 holes to finish")
        handicap = (
            self.player_handicap
            if self.player_handicap is not None
            else self._DEFAULT_HANDICAP
        )
        self.stableford_score = calculate_stableford(
            holes=self.holes,
            player_handicap=handicap,
            num_holes=num_holes,
            slope_rating=self.slope_rating,
            course_rating=self.course_rating,
        )
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
