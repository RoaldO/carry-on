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
    HYBRID_4 = "4h"
    HYBRID_5 = "5h"
    IRON_5 = "5i"
    IRON_6 = "6i"
    IRON_7 = "7i"
    IRON_8 = "8i"
    IRON_9 = "9i"
    PITCHING_WEDGE = "pw"
    GAP_WEDGE = "gw"
    SAND_WEDGE = "sw"
    LOB_WEDGE = "lw"
