from datetime import UTC, datetime
from importlib.resources import files

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

from carry_on.api.password_security import (
    hash_password,
    needs_rehash,
    verify_password as verify_password_hash,
    AuthenticatedUser,
    EmailCheck,
    ActivateRequest,
    LoginRequest,
)
from carry_on.infrastructure.repositories.mongo_user_repository import (
    get_users_collection,
)

load_dotenv()

app = FastAPI(title="CarryOn - Golf Stroke Tracker")


def verify_password(
    x_password: str = Header(None), x_email: str = Header(None)
) -> AuthenticatedUser:
    """Verify password from request header and return authenticated user.

    Authenticates user by verifying X-Email + X-Password headers against user's
    password hash in database.
    Returns AuthenticatedUser on success.
    """
    if not x_email or not x_password:
        raise HTTPException(status_code=401, detail="Authentication required")

    users_collection = get_users_collection()

    user = users_collection.find_one({"email": x_email.lower()})
    if not user or not verify_password_hash(x_password, user.get("pin_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Rehash if needed (on successful auth)
    if needs_rehash(user.get("pin_hash", "")):
        users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"pin_hash": hash_password(x_password)}}
        )

    return AuthenticatedUser(
        id=str(user["_id"]),
        email=user["email"],
        display_name=user.get("display_name", ""),
    )


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
    """Activate account by setting password."""
    users_collection = get_users_collection()

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    if user.get("activated_at"):
        raise HTTPException(status_code=400, detail="Account already activated")

    # Hash password before storing
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "pin_hash": hash_password(request.password),
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
    """Login with email and password."""
    users_collection = get_users_collection()

    user = users_collection.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("activated_at"):
        raise HTTPException(status_code=400, detail="Account not activated")

    # Check password using secure verification
    if not verify_password_hash(request.password, user.get("pin_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Rehash if using outdated algorithm
    if needs_rehash(user.get("pin_hash", "")):
        new_hash = hash_password(request.password)
        users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"pin_hash": new_hash}}
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


@app.get("/api/me")
async def get_current_user(user: AuthenticatedUser = Depends(verify_password)) -> dict:
    """Get current authenticated user's profile information."""
    return {
        "email": user.email,
        "display_name": user.display_name,
    }
