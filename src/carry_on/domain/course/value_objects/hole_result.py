from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HoleResult:
    """Result for a single hole in a round of golf.

    Immutable value object representing the strokes taken on a hole,
    along with the hole's par and stroke index (handicap allocation order).
    """

    hole_number: int
    strokes: int
    par: int
    stroke_index: int
    stableford_points: int | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.hole_number <= 18:
            raise ValueError("Hole number must be between 1 and 18")
        if self.strokes < 1:
            raise ValueError("Strokes must be at least 1")
        if self.par not in (3, 4, 5):
            raise ValueError("Par must be 3, 4, or 5")
        if not 1 <= self.stroke_index <= 18:
            raise ValueError("Stroke index must be between 1 and 18")
