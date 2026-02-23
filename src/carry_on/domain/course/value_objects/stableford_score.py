from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StablefordScore:
    """Total Stableford points scored in a round of golf.

    Immutable value object representing the aggregate Stableford score.
    Points are always non-negative.
    """

    points: int

    def __post_init__(self) -> None:
        if self.points < 0:
            raise ValueError("Points must not be negative")
