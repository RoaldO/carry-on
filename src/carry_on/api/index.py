from datetime import UTC, date as date_type, datetime
from importlib.resources import files
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from pymongo.collection import Collection

from carry_on.api.pin_security import (
    hash_pin,
    needs_rehash,
    verify_pin as verify_pin_hash,
)
from carry_on.infrastructure.mongodb import get_database
from carry_on.infrastructure.repositories.mongo_stroke_repository import (
    MongoStrokeRepository,
    get_strokes_collection,
)
from carry_on.infrastructure.repositories.mongo_user_repository import get_users_collection
from carry_on.services.stroke_service import StrokeService

load_dotenv()

app = FastAPI(title="CarryOn - Golf Stroke Tracker")


def get_ideas_collection() -> Collection:
    """Get MongoDB ideas collection, initializing connection if needed."""
    return get_database().ideas


def get_stroke_service() -> StrokeService:
    """Get StrokeService with MongoDB repository."""
    collection = get_strokes_collection()
    repository = MongoStrokeRepository(collection)
    return StrokeService(repository)


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user returned by verify_pin()."""
    id: str
    email: str
    display_name: str


def verify_pin(
    x_pin: str = Header(None), x_email: str = Header(None)
) -> AuthenticatedUser:
    """Verify PIN from request header and return authenticated user.

    Authenticates user by verifying X-Email + X-Pin headers against user's PIN in
    database.
    Returns AuthenticatedUser on success.
    """
    if not x_email or not x_pin:
        raise HTTPException(status_code=401, detail="Authentication required")

    users_collection = get_users_collection()

    user = users_collection.find_one({"email": x_email.lower()})
    if not user or not verify_pin_hash(x_pin, user.get("pin_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    # Rehash if needed (on successful auth)
    if needs_rehash(user.get("pin_hash", "")):
        users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"pin_hash": hash_pin(x_pin)}}
        )

    return AuthenticatedUser(
        id=str(user["_id"]),
        email=user["email"],
        display_name=user.get("display_name", ""),
    )


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


class IdeaCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)


class EmailCheck(BaseModel):
    email: str = Field(..., min_length=1)


class ActivateRequest(BaseModel):
    email: str = Field(..., min_length=1)
    pin: str = Field(..., min_length=4, max_length=10)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    pin: str = Field(..., min_length=4, max_length=10)


@app.post("/api/check-email")
async def check_email(request: EmailCheck) -> dict:
    """Check if email exists and get activation status."""
    users_collection = get_users_collection()

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    status = "activated" if user.get("activated_at") else "needs_activation"
    return {
        "status": status,
        "display_name": user.get("display_name", ""),
    }


@app.post("/api/activate")
async def activate_account(request: ActivateRequest) -> dict:
    """Activate account by setting PIN."""
    users_collection = get_users_collection()

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    if user.get("activated_at"):
        raise HTTPException(status_code=400, detail="Account already activated")

    # Hash PIN before storing
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "pin_hash": hash_pin(request.pin),
                "activated_at": datetime.now(UTC).isoformat(),
            }
        },
    )

    return {
        "message": "Account activated successfully",
        "user": {
            "email": user["email"],
            "display_name": user.get("display_name", ""),
        },
    }


@app.post("/api/login")
async def login(request: LoginRequest) -> dict:
    """Login with email and PIN."""
    users_collection = get_users_collection()

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    if not user.get("activated_at"):
        raise HTTPException(status_code=400, detail="Account not activated")

    # Check PIN using secure verification
    if not verify_pin_hash(request.pin, user.get("pin_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    # Rehash if using outdated algorithm
    if needs_rehash(user.get("pin_hash", "")):
        users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"pin_hash": hash_pin(request.pin)}}
        )

    return {
        "message": "Login successful",
        "user": {
            "email": user["email"],
            "display_name": user.get("display_name", ""),
        },
    }


@app.get("/", response_class=HTMLResponse)
async def serve_form() -> str:
    """Serve the golf stroke entry form."""
    static_files = files("carry_on.static")
    return (static_files / "index.html").read_text(encoding="utf-8")


@app.get("/ideas")
async def serve_ideas() -> RedirectResponse:
    """Redirect /ideas to /#ideas for tab navigation."""
    return RedirectResponse(url="/#ideas", status_code=302)


@app.get("/api/me")
async def get_current_user(user: AuthenticatedUser = Depends(verify_pin)) -> dict:
    """Get current authenticated user's profile information."""
    return {
        "email": user.email,
        "display_name": user.display_name,
    }


@app.post("/api/strokes")
async def create_stroke(
    stroke: StrokeCreate,
    user: AuthenticatedUser = Depends(verify_pin),
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
    user: AuthenticatedUser = Depends(verify_pin),
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


@app.post("/api/ideas")
async def create_idea(
    idea: IdeaCreate, user: AuthenticatedUser = Depends(verify_pin)
) -> dict:
    """Submit a new idea."""
    ideas_collection = get_ideas_collection()

    created_at = datetime.now(UTC).isoformat()
    doc = {
        "description": idea.description,
        "created_at": created_at,
        "user_id": user.id,
    }

    result = ideas_collection.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "message": "Idea submitted successfully",
        "idea": {
            "description": idea.description,
            "created_at": created_at,
        },
    }


@app.get("/api/ideas")
async def list_ideas(
    limit: int = 50, user: AuthenticatedUser = Depends(verify_pin)
) -> dict:
    """List submitted ideas for the authenticated user."""
    ideas_collection = get_ideas_collection()

    ideas = []
    cursor = (
        ideas_collection.find({"user_id": user.id}).sort("created_at", -1).limit(limit)
    )

    for doc in cursor:
        ideas.append(
            {
                "id": str(doc["_id"]),
                "description": doc["description"],
                "created_at": doc["created_at"],
            }
        )

    return {"ideas": ideas, "count": len(ideas)}
