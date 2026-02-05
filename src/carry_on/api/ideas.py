from fastapi import Depends, HTTPException

from carry_on.api.index import app, verify_password
from carry_on.api.schema import IdeaCreate
from carry_on.services.authentication_service import AuthenticatedUser
from carry_on.services.idea_service import IdeaService, get_ideas_service


@app.post("/api/ideas")
async def create_idea(
    idea: IdeaCreate,
    user: AuthenticatedUser = Depends(verify_password),
    service: IdeaService = Depends(get_ideas_service),
) -> dict:
    """Submit a new idea."""
    try:
        idea_id = service.record_idea(
            user_id=user.id,
            description=idea.description,
        )
    except ValueError as e:
        # Missing description
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": idea_id.value,
        "message": "Idea submitted successfully",
        "idea": {
            "description": idea.description,
        },
    }
