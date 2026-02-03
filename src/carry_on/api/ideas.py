from datetime import datetime, UTC
from typing import NotRequired, TypedDict

from bson import ObjectId
from fastapi import Depends
from pydantic import BaseModel, Field
from pymongo.synchronous.collection import Collection

from carry_on.api.index import app, verify_password
from carry_on.api.password_security import AuthenticatedUser
from carry_on.infrastructure.mongodb import get_database


class IdeaDoc(TypedDict):
    _id: NotRequired[ObjectId]
    description: str
    created_at: str
    user_id: str


class IdeaCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)


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
