from datetime import datetime, UTC

from fastapi import Depends
from pymongo.synchronous.collection import Collection

from carry_on.api.index import app, verify_password
from carry_on.api.password_security import AuthenticatedUser
from carry_on.api.schema import IdeaCreate, IdeaDoc
from carry_on.infrastructure.mongodb import get_database


@app.post("/api/ideas")
async def create_idea(
    idea: IdeaCreate, user: AuthenticatedUser = Depends(verify_password)
) -> dict:
    """Submit a new idea."""
    ideas_collection = get_ideas_collection()

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


def get_ideas_collection() -> Collection[IdeaDoc]:
    """Get MongoDB ideas collection, initializing connection if needed."""
    return get_database().ideas
