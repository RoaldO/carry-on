from importlib.resources import files

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

from carry_on.api.schema import (
    ActivateRequest,
    EmailCheck,
    LoginRequest,
    UpdatePasswordRequest,
)
from carry_on.domain.exceptions import (
    AccountAlreadyActivatedError,
    AccountNotActivatedError,
    InvalidCredentialsError,
    PasswordNotCompliantError,
    UserNotFoundError,
)
from carry_on.services.authentication_service import (
    AuthenticatedUser,
    AuthenticationService,
    get_authentication_service,
)

load_dotenv()

app = FastAPI(title="CarryOn - Golf Stroke Tracker")


def verify_password(
    x_password: str = Header(None),
    x_email: str = Header(None),
    auth_service: AuthenticationService = Depends(get_authentication_service),
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
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@app.post("/api/check-email")
async def check_email(
    request: EmailCheck,
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> dict:
    """Check if email exists and get activation status."""
    try:
        result = auth_service.check_email(request.email)
        return {
            "status": result.status,
            "display_name": result.display_name,
        }
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")


@app.post("/api/activate")
async def activate_account(
    request: ActivateRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
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
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")
    except AccountAlreadyActivatedError:
        raise HTTPException(status_code=400, detail="Account already activated")


@app.post("/api/login")
async def login(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
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
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except AccountNotActivatedError:
        raise HTTPException(status_code=400, detail="Account not activated")


@app.post("/api/update-password")
async def update_password(
    request: UpdatePasswordRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
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
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid current password")
    except PasswordNotCompliantError:
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
async def get_current_user(user: AuthenticatedUser = Depends(verify_password)) -> dict:
    """Get current authenticated user's profile information."""
    return {
        "email": user.email,
        "display_name": user.display_name,
    }
