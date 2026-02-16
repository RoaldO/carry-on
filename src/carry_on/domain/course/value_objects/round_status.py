"""RoundStatus value object representing the state of a round."""

from enum import Enum


class RoundStatus(str, Enum):
    """Round status with short string values for serialization.

    Using str, Enum inheritance enables:
    - Direct JSON serialization to string values
    - String comparison (RoundStatus.IN_PROGRESS == "ip")
    - Lookup by value (RoundStatus("ip"))

    Valid states:
    - IN_PROGRESS: Round is actively being played
    - FINISHED: Round completed successfully (may be <18 holes)
    - ABORTED: Round abandoned/cancelled
    """

    IN_PROGRESS = "ip"
    FINISHED = "f"
    ABORTED = "a"
