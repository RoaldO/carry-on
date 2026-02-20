"""Handicap value object representing a golfer's WHS handicap index."""

from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Handicap:
    """Immutable value object representing a golf handicap index.

    The World Handicap System (WHS) defines handicap indices from
    -10.0 (exceptional plus handicap) to 54.0 (maximum for beginners).

    Attributes:
        value: Handicap index as Decimal for precision.

    Raises:
        ValueError: If value is outside the valid WHS range.
    """

    value: Decimal

    MIN_VALUE: ClassVar[Decimal] = Decimal("-10.0")
    MAX_VALUE: ClassVar[Decimal] = Decimal("54.0")

    def __post_init__(self) -> None:
        """Validate handicap is within WHS range."""
        if not self.MIN_VALUE <= self.value <= self.MAX_VALUE:
            raise ValueError(
                f"Handicap must be {self.MIN_VALUE} to {self.MAX_VALUE}, "
                f"got {self.value}"
            )
