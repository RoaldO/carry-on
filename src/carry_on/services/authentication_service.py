"""AuthenticationService for user authentication operations."""

from dataclasses import dataclass
from datetime import UTC, datetime

from carry_on.domain.exceptions import (
    AccountAlreadyActivatedError,
    AccountNotActivatedError,
    InvalidCredentialsError,
    PasswordNotCompliantError,
    UserNotFoundError,
)
from carry_on.domain.repositories.user_repository import UserRepository
from carry_on.domain.security.password_hasher import PasswordHasher
from carry_on.infrastructure.repositories.mongo_user_repository import (
    MongoUserRepository,
    get_users_collection,
)
from carry_on.infrastructure.security.argon2_password_hasher import (
    get_password_hasher,
)


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Represents an authenticated user."""

    id: str
    email: str
    display_name: str


@dataclass(frozen=True, slots=True)
class EmailCheckResult:
    """Result of an email check operation."""

    status: str  # "activated" or "needs_activation"
    display_name: str


@dataclass(frozen=True, slots=True)
class LoginResult:
    """Result of a login operation."""

    status: str  # "success" or "password_update_required"
    user: AuthenticatedUser
    message: str = ""


class AuthenticationService:
    """Application service for authentication operations.

    Handles user authentication, account activation, and password management.
    Delegates persistence to the repository and hashing to the hasher.
    """

    def __init__(self, repository: UserRepository, hasher: PasswordHasher) -> None:
        """Initialize the service with dependencies.

        Args:
            repository: The user repository for persistence operations.
            hasher: The password hasher for hashing operations.
        """
        self._repository = repository
        self._hasher = hasher

    def check_email(self, email: str) -> EmailCheckResult:
        """Check if an email exists and get activation status.

        Args:
            email: The email address to check.

        Returns:
            EmailCheckResult with status and display name.

        Raises:
            UserNotFoundError: If the email doesn't exist.
        """
        user = self._repository.find_by_email(email.lower())
        if user is None:
            raise UserNotFoundError(email)

        status = "activated" if user.is_activated else "needs_activation"
        return EmailCheckResult(status=status, display_name=user.display_name)

    def activate_account(self, email: str, password: str) -> AuthenticatedUser:
        """Activate an account by setting a password.

        Args:
            email: The email address of the account to activate.
            password: The password to set.

        Returns:
            AuthenticatedUser on successful activation.

        Raises:
            UserNotFoundError: If the email doesn't exist.
            AccountAlreadyActivatedError: If the account is already activated.
        """
        user = self._repository.find_by_email(email.lower())
        if user is None:
            raise UserNotFoundError(email)

        if user.is_activated:
            raise AccountAlreadyActivatedError(email)

        # Hash password and activate
        password_hash = self._hasher.hash(password)
        activated_user = user.activate(password_hash, datetime.now(UTC))
        self._repository.save(activated_user)

        return AuthenticatedUser(
            id=user.id.value if user.id else "",
            email=user.email,
            display_name=user.display_name,
        )

    def login(self, email: str, password: str) -> LoginResult:
        """Login with email and password.

        Args:
            email: The email address.
            password: The password.

        Returns:
            LoginResult with status and user info.

        Raises:
            InvalidCredentialsError: If email doesn't exist or password is wrong.
            AccountNotActivatedError: If the account is not activated.
        """
        user = self._repository.find_by_email(email.lower())
        if user is None:
            raise InvalidCredentialsError()

        if not user.is_activated:
            raise AccountNotActivatedError(email)

        # Verify password
        if not self._hasher.verify(password, user.password_hash or ""):
            raise InvalidCredentialsError()

        # Rehash if using outdated algorithm
        if self._hasher.needs_rehash(user.password_hash or ""):
            new_hash = self._hasher.hash(password)
            updated_user = user.update_password_hash(new_hash)
            self._repository.save(updated_user)

        # Check password compliance
        authenticated_user = AuthenticatedUser(
            id=user.id.value if user.id else "",
            email=user.email,
            display_name=user.display_name,
        )

        if not self._hasher.is_compliant(password):
            return LoginResult(
                status="password_update_required",
                user=authenticated_user,
                message="Password does not meet complexity requirements",
            )

        return LoginResult(
            status="success",
            user=authenticated_user,
            message="Login successful",
        )

    def update_password(
        self, email: str, current_password: str, new_password: str
    ) -> None:
        """Update a user's password.

        Args:
            email: The email address.
            current_password: The current password for verification.
            new_password: The new password to set.

        Raises:
            UserNotFoundError: If the email doesn't exist.
            InvalidCredentialsError: If the current password is wrong.
            PasswordNotCompliantError: If the new password doesn't meet requirements.
        """
        user = self._repository.find_by_email(email.lower())
        if user is None:
            raise UserNotFoundError(email)

        # Verify current password
        if not self._hasher.verify(current_password, user.password_hash or ""):
            raise InvalidCredentialsError()

        # Check new password compliance
        if not self._hasher.is_compliant(new_password):
            raise PasswordNotCompliantError(
                "New password must be at least 8 characters"
            )

        # Hash and save new password
        new_hash = self._hasher.hash(new_password)
        updated_user = user.update_password_hash(new_hash)
        self._repository.save(updated_user)

    def authenticate(self, email: str, password: str) -> AuthenticatedUser:
        """Authenticate a user by email and password (for header auth).

        This is used for X-Email/X-Password header authentication.

        Args:
            email: The email address.
            password: The password.

        Returns:
            AuthenticatedUser on success.

        Raises:
            InvalidCredentialsError: If email doesn't exist or password is wrong.
        """
        user = self._repository.find_by_email(email.lower())
        if user is None:
            raise InvalidCredentialsError()

        # Verify password
        if not self._hasher.verify(password, user.password_hash or ""):
            raise InvalidCredentialsError()

        # Rehash if using outdated algorithm
        if self._hasher.needs_rehash(user.password_hash or ""):
            new_hash = self._hasher.hash(password)
            updated_user = user.update_password_hash(new_hash)
            self._repository.save(updated_user)

        return AuthenticatedUser(
            id=user.id.value if user.id else "",
            email=user.email,
            display_name=user.display_name,
        )


def get_authentication_service() -> AuthenticationService:
    """Get AuthenticationService with MongoDB repository and Argon2 hasher.

    Returns:
        An AuthenticationService instance with production dependencies.
    """
    collection = get_users_collection()
    repository = MongoUserRepository(collection)
    hasher = get_password_hasher()
    return AuthenticationService(repository, hasher)
