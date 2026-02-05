from typing import NotRequired, TypedDict

from bson import ObjectId
from pydantic import BaseModel, Field

from carry_on.domain.security.password_hasher import MIN_PASSWORD_LENGTH


# Authentication request models


class EmailCheck(BaseModel):
    """Request model for checking email existence."""

    email: str = Field(..., min_length=1)


class ActivateRequest(BaseModel):
    """Request model for account activation."""

    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)


class LoginRequest(BaseModel):
    """Request model for login."""

    email: str = Field(..., min_length=1)
    # min_length=4 allows legacy PINs for migration flow
    password: str = Field(..., min_length=4)


class UpdatePasswordRequest(BaseModel):
    """Request model for password update."""

    email: str = Field(..., min_length=1)
    current_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)


# Idea models


class IdeaCreate(BaseModel):
    """Request model for creating an idea."""

    description: str = Field(..., min_length=1, max_length=1000)


class IdeaDoc(TypedDict):
    """MongoDB document schema for ideas."""

    _id: NotRequired[ObjectId]
    description: str
    created_at: str
    user_id: str
