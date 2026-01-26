"""Distance value object representing golf shot distance in meters."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Distance:
    """Immutable value object representing golf shot distance.

    Attributes:
        meters: Distance in meters (0-400 range).

    Raises:
        ValueError: If meters is outside valid range.
    """

    meters: int

    MIN_METERS: ClassVar[int] = 0
    MAX_METERS: ClassVar[int] = 400

    def __post_init__(self) -> None:
        """Validate distance is within acceptable range."""
        if not self.MIN_METERS <= self.meters <= self.MAX_METERS:
            raise ValueError(
                f"Distance must be {self.MIN_METERS}-{self.MAX_METERS}m, "
                f"got {self.meters}m"
            )
