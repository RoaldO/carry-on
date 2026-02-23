from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from carry_on.domain.core.value_objects.identifier import Identifier
from carry_on.domain.course.value_objects.hole import Hole


@dataclass(frozen=True, slots=True)
class CourseId(Identifier):
    """Unique identifier for a Course aggregate."""


@dataclass
class Course:
    """A golf course with its hole specifications.

    Aggregate root that models the layout of a golf course,
    including the par and stroke index for each hole.
    """

    id: CourseId | None
    name: str
    holes: tuple[Hole, ...]
    slope_rating: Decimal | None = None
    course_rating: Decimal | None = None

    @classmethod
    def create(
        cls,
        name: str,
        holes: tuple[Hole, ...],
        id: CourseId | None = None,
        slope_rating: Decimal | None = None,
        course_rating: Decimal | None = None,
    ) -> Self:
        return cls(
            id=id,
            name=name,
            holes=holes,
            slope_rating=slope_rating,
            course_rating=course_rating,
        )

    def __post_init__(self) -> None:
        """Validate and enforce business rules."""
        self._validate()

    def _validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Course name required")

        n = len(self.holes)
        if n not in (9, 18):
            raise ValueError("Course must have exactly 9 or 18 holes")

        hole_numbers = sorted(h.hole_number for h in self.holes)
        if hole_numbers != list(range(1, n + 1)):
            raise ValueError(f"Hole numbers must be sequential from 1 to {n}")

        stroke_indices = sorted(h.stroke_index for h in self.holes)
        if stroke_indices != list(range(1, n + 1)):
            raise ValueError(f"Stroke indices must be unique and cover 1 to {n}")

        if self.slope_rating is not None:
            if not (Decimal("55") <= self.slope_rating <= Decimal("155")):
                raise ValueError("Slope rating must be between 55 and 155")

        if self.course_rating is not None:
            if self.course_rating <= Decimal("0"):
                raise ValueError("Course rating must be positive")

    @property
    def total_par(self) -> int:
        """Sum of par across all holes."""
        return sum(h.par for h in self.holes)

    @property
    def number_of_holes(self) -> int:
        """Number of holes on the course (9 or 18)."""
        return len(self.holes)
