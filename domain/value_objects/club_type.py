"""ClubType value object representing golf club types."""

from enum import Enum


class ClubType(str, Enum):
    """Golf club types with short string values for serialization.

    Using str, Enum inheritance enables:
    - Direct JSON serialization to string values
    - String comparison (ClubType.DRIVER == "d")
    - Lookup by value (ClubType("d"))
    """

    DRIVER = "d"
    WOOD_3 = "3w"
    WOOD_5 = "5w"
    HYBRID_4 = "h4"
    HYBRID_5 = "h5"
    IRON_5 = "i5"
    IRON_6 = "i6"
    IRON_7 = "i7"
    IRON_8 = "i8"
    IRON_9 = "i9"
    PITCHING_WEDGE = "pw"
    GAP_WEDGE = "gw"
    SAND_WEDGE = "sw"
    LOB_WEDGE = "lw"
