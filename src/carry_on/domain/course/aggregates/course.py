from dataclasses import dataclass
from typing import Self

from carry_on.domain.course.value_objects.hole import Hole


@dataclass(frozen=True, slots=True)
class CourseId:
    """Unique identifier for a Course aggregate.

    Immutable value object wrapping the database ID.
    """

    value: str


@dataclass
class Course:
    """A golf course with its hole specifications.

    Aggregate root that models the layout of a golf course,
    including the par and stroke index for each hole.
    """

    id: CourseId | None
    name: str
    holes: tuple[Hole, ...]

    @classmethod
    def create(
        cls,
        name: str,
        holes: tuple[Hole, ...],
        id: CourseId | None = None,
    ) -> Self:
        return cls(id=id, name=name, holes=holes)

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

    @property
    def total_par(self) -> int:
        """Sum of par across all holes."""
        return sum(h.par for h in self.holes)

    @property
    def number_of_holes(self) -> int:
        """Number of holes on the course (9 or 18)."""
        return len(self.holes)
