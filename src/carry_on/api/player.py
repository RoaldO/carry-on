"""Player API endpoints for the player bounded context."""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException

from carry_on.api.index import app, verify_password
from carry_on.api.schema import UpdateHandicapRequest
from carry_on.container import Container
from carry_on.services.authentication_service import AuthenticatedUser
from carry_on.services.player_service import PlayerService


@app.get("/api/player/me")
@inject
async def get_player(
    user: AuthenticatedUser = Depends(verify_password),
    service: PlayerService = Depends(Provide[Container.player_service]),
) -> dict:
    """Get the authenticated user's player profile."""
    player = service.get_player(user.id)

    return {
        "handicap": str(player.handicap.value) if player and player.handicap else None,
    }


@app.put("/api/player/handicap")
@inject
async def update_handicap(
    request: UpdateHandicapRequest,
    user: AuthenticatedUser = Depends(verify_password),
    service: PlayerService = Depends(Provide[Container.player_service]),
) -> dict:
    """Update the authenticated user's handicap."""
    try:
        service.update_handicap(user.id, request.handicap)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Handicap updated successfully"}
