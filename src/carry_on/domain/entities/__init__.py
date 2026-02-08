"""Domain entities for CarryOn golf application."""

from carry_on.domain.training.entities.stroke import Stroke, StrokeId
from carry_on.domain.entities.user import User, UserId

__all__ = ["Stroke", "StrokeId", "User", "UserId"]
