"""Domain exceptions for authentication and user operations."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found by email or ID."""

    def __init__(self, email: str | None = None) -> None:
        self.email = email
        message = f"User not found: {email}" if email else "User not found"
        super().__init__(message)


class InvalidCredentialsError(Exception):
    """Raised when authentication fails due to invalid credentials."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class AccountNotActivatedError(Exception):
    """Raised when trying to login with an account that hasn't been activated."""

    def __init__(self, email: str | None = None) -> None:
        self.email = email
        message = (
            f"Account not activated: {email}" if email else "Account not activated"
        )
        super().__init__(message)


class AccountAlreadyActivatedError(Exception):
    """Raised when trying to activate an already activated account."""

    def __init__(self, email: str | None = None) -> None:
        self.email = email
        message = (
            f"Account already activated: {email}"
            if email
            else "Account already activated"
        )
        super().__init__(message)


class PasswordNotCompliantError(Exception):
    """Raised when a password doesn't meet complexity requirements."""

    def __init__(
        self, reason: str = "Password does not meet complexity requirements"
    ) -> None:
        self.reason = reason
        super().__init__(reason)
