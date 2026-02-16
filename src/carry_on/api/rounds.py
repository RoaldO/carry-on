"""API endpoints for round management."""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from carry_on.api.index import app, verify_password
from carry_on.container import Container
from carry_on.domain.course.aggregates.round import RoundId
from carry_on.services.authentication_service import AuthenticatedUser
from carry_on.services.round_service import RoundService


class HoleResultRequest(BaseModel):
    hole_number: int
    strokes: int
    par: int
    stroke_index: int


class HoleUpdateRequest(BaseModel):
    strokes: int
    par: int
    stroke_index: int


class RoundCreateRequest(BaseModel):
    course_name: str
    date: str
    holes: list[HoleResultRequest] = []


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


@app.get("/api/rounds/{round_id}")
@inject
async def get_round(
    round_id: str,
    user: AuthenticatedUser = Depends(verify_password),
    service: RoundService = Depends(Provide[Container.round_service]),
) -> dict:
    """Get a specific round by ID."""
    round = service.get_round(user.id, RoundId(value=round_id))
    if round is None:
        raise HTTPException(status_code=404, detail="Round not found")

    return {
        "id": round.id.value if round.id else None,
        "course_name": round.course_name,
        "date": round.date.isoformat(),
        "holes": [
            {
                "hole_number": h.hole_number,
                "strokes": h.strokes,
                "par": h.par,
                "stroke_index": h.stroke_index,
            }
            for h in round.holes
        ],
        "is_complete": round.is_complete,
    }


@app.patch("/api/rounds/{round_id}/holes/{hole_number}")
@inject
async def update_hole(
    round_id: str,
    hole_number: int,
    hole_data: HoleUpdateRequest,
    user: AuthenticatedUser = Depends(verify_password),
    service: RoundService = Depends(Provide[Container.round_service]),
) -> dict:
    """Update a single hole result."""
    try:
        service.update_hole(
            user_id=user.id,
            round_id=RoundId(value=round_id),
            hole={
                "hole_number": hole_number,
                "strokes": hole_data.strokes,
                "par": hole_data.par,
                "stroke_index": hole_data.stroke_index,
            },
        )
        return {"message": "Hole updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
