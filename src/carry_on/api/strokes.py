from datetime import date as date_type
from typing import Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from carry_on.api.index import app, verify_password
from carry_on.api.password_security import AuthenticatedUser
from carry_on.infrastructure.repositories import MongoStrokeRepository
from carry_on.infrastructure.repositories.mongo_stroke_repository import (
    get_strokes_collection,
)
from carry_on.services import StrokeService


def get_stroke_service() -> StrokeService:
    """Get StrokeService with MongoDB repository."""
    collection = get_strokes_collection()
    repository = MongoStrokeRepository(collection)
    return StrokeService(repository)


class StrokeCreate(BaseModel):
    club: str
    distance: Optional[int] = None
    fail: bool = False
    date: date_type = Field(default_factory=date_type.today)


class Stroke(BaseModel):
    id: str
    club: str
    distance: Optional[int] = None
    fail: bool = False


@app.post("/api/strokes")
async def create_stroke(
    stroke: StrokeCreate,
    user: AuthenticatedUser = Depends(verify_password),
    service: StrokeService = Depends(get_stroke_service),
) -> dict:
    """Record a new golf stroke."""
    try:
        stroke_id = service.record_stroke(
            user_id=user.id,
            club=stroke.club,
            stroke_date=stroke.date,
            distance=stroke.distance,
            fail=stroke.fail,
        )
    except ValueError as e:
        # Invalid club or missing distance
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": stroke_id.value,
        "message": "Stroke recorded successfully",
        "stroke": {
            "club": stroke.club,
            "distance": stroke.distance if not stroke.fail else None,
            "fail": stroke.fail,
            "date": stroke.date.isoformat(),
        },
    }


@app.get("/api/strokes")
async def list_strokes(
    limit: int = 20,
    user: AuthenticatedUser = Depends(verify_password),
    service: StrokeService = Depends(get_stroke_service),
) -> dict:
    """List recent strokes for the authenticated user."""
    strokes = service.get_user_strokes(user.id, limit)

    return {
        "strokes": [
            {
                "id": stroke.id.value if stroke.id else None,
                "club": stroke.club.value,
                "distance": stroke.distance.meters if stroke.distance else None,
                "fail": stroke.fail,
                "date": stroke.stroke_date.isoformat(),
                "created_at": stroke.created_at.isoformat()
                if stroke.created_at
                else None,
            }
            for stroke in strokes
        ],
        "count": len(strokes),
    }
