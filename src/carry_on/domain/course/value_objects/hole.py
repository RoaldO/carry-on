from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Hole:
    """Specification for a single hole on a golf course.

    Immutable value object representing the hole's number, par,
    and stroke index (handicap allocation order).
    """

    hole_number: int
    par: int
    stroke_index: int

    def __post_init__(self) -> None:
        if not 1 <= self.hole_number <= 18:
            raise ValueError("Hole number must be between 1 and 18")
        if self.par not in (3, 4, 5):
            raise ValueError("Par must be 3, 4, or 5")
        if not 1 <= self.stroke_index <= 18:
            raise ValueError("Stroke index must be between 1 and 18")
