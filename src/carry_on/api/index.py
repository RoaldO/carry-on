"""Web API for CarryOn application."""

import os
from importlib.resources import files

import sentry_sdk
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

from carry_on.api import schema as api_schema
from carry_on.container import Container
from carry_on.domain import exceptions as domain_exceptions
from carry_on.services.authentication_service import (
    AuthenticatedUser,
    AuthenticationService,
)

load_dotenv()

# Initialize Sentry for error tracking (only if DSN is configured)
sentry_dsn = os.getenv("SENTRY_DSN")
_env_mapping = {
    "production": "production",
    "preview": "staging",
    "development": "development",
}
if sentry_dsn:  # pragma: no cover
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set traces_sample_rate to capture performance data
        # Adjust in production based on traffic volume
        traces_sample_rate=0.1,
        # Capture 100% of errors
        sample_rate=1.0,
        # Associate errors with releases (set via SENTRY_RELEASE env var)
        # release=os.getenv("SENTRY_RELEASE"),
        release=os.getenv("VERCEL_GIT_COMMIT_SHA"),
        # Set environment (production, staging, development)
        # environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        environment=_env_mapping[os.getenv("VERCEL_ENV", "production")],
    )

app = FastAPI(title="CarryOn - Golf Stroke Tracker")


@inject
def verify_password(
    x_password: str = Header(None),
    x_email: str = Header(None),
    auth_service: AuthenticationService = Depends(
        Provide[Container.authentication_service]
    ),
) -> AuthenticatedUser:
    """Verify password from request header and return authenticated user.

    Authenticates user by verifying X-Email + X-Password headers against user's
    password hash in database.
    Returns AuthenticatedUser on success.
    """
    if not x_email or not x_password:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        return auth_service.authenticate(x_email, x_password)
    except domain_exceptions.InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@app.post("/api/check-email")
@inject
async def check_email(
    request: api_schema.EmailCheck,
    auth_service: AuthenticationService = Depends(
        Provide[Container.authentication_service]
    ),
) -> dict:
    """Check if email exists and get activation status."""
    try:
        result = auth_service.check_email(request.email)
        return {
            "status": result.status,
            "display_name": result.display_name,
        }
    except domain_exceptions.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")


@app.post("/api/activate")
@inject
async def activate_account(
    request: api_schema.ActivateRequest,
    auth_service: AuthenticationService = Depends(
        Provide[Container.authentication_service]
    ),
) -> dict:
    """Activate account by setting password."""
    try:
        user = auth_service.activate_account(request.email, request.password)
        return {
            "message": "Account activated successfully",
            "user": {
                "email": user.email,
                "display_name": user.display_name,
            },
        }
    except domain_exceptions.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")
    except domain_exceptions.AccountAlreadyActivatedError:
        raise HTTPException(status_code=400, detail="Account already activated")


@app.post("/api/login")
@inject
async def login(
    request: api_schema.LoginRequest,
    auth_service: AuthenticationService = Depends(
        Provide[Container.authentication_service]
    ),
) -> dict:
    """Login with email and password."""
    try:
        result = auth_service.login(request.email, request.password)
        return {
            "status": result.status,
            "message": result.message,
            "user": {
                "email": result.user.email,
                "display_name": result.user.display_name,
            },
        }
    except domain_exceptions.InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except domain_exceptions.AccountNotActivatedError:
        raise HTTPException(status_code=400, detail="Account not activated")


@app.post("/api/update-password")
@inject
async def update_password(
    request: api_schema.UpdatePasswordRequest,
    auth_service: AuthenticationService = Depends(
        Provide[Container.authentication_service]
    ),
) -> dict:
    """Update password for users with weak passwords."""
    try:
        auth_service.update_password(
            request.email, request.current_password, request.new_password
        )
        return {
            "status": "success",
            "message": "Password updated successfully",
        }
    except domain_exceptions.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")
    except domain_exceptions.InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid current password")
    except domain_exceptions.PasswordNotCompliantError:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters",
        )


@app.get("/", response_class=HTMLResponse)
async def serve_form() -> str:
    """Serve the golf stroke entry form."""
    static_files = files("carry_on.static")
    return (static_files / "index.html").read_text(encoding="utf-8")


@app.get("/api/me")
async def get_current_user(
    user: AuthenticatedUser = Depends(verify_password),
) -> dict:
    """Get current authenticated user's profile information."""
    return {
        "email": user.email,
        "display_name": user.display_name,
    }
