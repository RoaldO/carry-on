"""API endpoints for round management."""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from carry_on.api.index import app, verify_password
from carry_on.container import Container
from carry_on.services.authentication_service import AuthenticatedUser
from carry_on.services.round_service import RoundService


class HoleResultRequest(BaseModel):
    hole_number: int
    strokes: int
    par: int
    stroke_index: int


class RoundCreateRequest(BaseModel):
    course_name: str
    date: str
    holes: list[HoleResultRequest]


@app.post("/api/rounds")
@inject
async def create_round(
    round_data: RoundCreateRequest,
    user: AuthenticatedUser = Depends(verify_password),
    service: RoundService = Depends(Provide[Container.round_service]),
) -> dict:
    """Record a new golf round."""
    try:
        round_id = service.create_round(
            user_id=user.id,
            course_name=round_data.course_name,
            date=round_data.date,
            holes=[h.model_dump() for h in round_data.holes],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": round_id.value,
        "message": "Round recorded successfully",
    }


@app.get("/api/rounds")
@inject
async def list_rounds(
    user: AuthenticatedUser = Depends(verify_password),
    service: RoundService = Depends(Provide[Container.round_service]),
) -> dict:
    """List rounds for the authenticated user."""
    rounds = service.get_user_rounds(user.id)

    return {
        "rounds": [
            {
                "id": r.id.value if r.id else None,
                "course_name": r.course_name,
                "date": r.date.isoformat(),
                "total_strokes": r.total_strokes,
                "holes_played": len(r.holes),
            }
            for r in rounds
        ],
        "count": len(rounds),
    }
