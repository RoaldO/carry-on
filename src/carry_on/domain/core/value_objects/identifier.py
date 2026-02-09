from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Identifier:
    """Unique identifier entities and aggregates.

    Immutable value object wrapping the database ID.
    """

    value: str
