from typing import TypedDict, NotRequired

from bson import ObjectId
from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)


class IdeaDoc(TypedDict):
    _id: NotRequired[ObjectId]
    description: str
    created_at: str
    user_id: str
