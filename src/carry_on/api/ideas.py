from datetime import datetime, UTC

from fastapi import Depends

from carry_on.api.index import app, verify_password
from carry_on.api.password_security import AuthenticatedUser
from carry_on.api.schema import IdeaCreate, IdeaDoc
from carry_on import bootstrap, MongodbDatabase


@app.post("/api/ideas")
async def create_idea(
    idea: IdeaCreate, user: AuthenticatedUser = Depends(verify_password)
) -> dict:
    """Submit a new idea."""
    ideas_collection = bootstrap.get(MongodbDatabase).get_ideas()

    created_at = datetime.now(UTC).isoformat()
    doc = IdeaDoc(
        description=idea.description,
        created_at=created_at,
        user_id=user.id,
    )

    result = ideas_collection.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "message": "Idea submitted successfully",
        "idea": {
            "description": idea.description,
            "created_at": created_at,
        },
    }
