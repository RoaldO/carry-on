"""Tests for AuthenticationService."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import allure
import pytest

from carry_on.domain.entities.user import User, UserId
from carry_on.domain.exceptions import (
    AccountAlreadyActivatedError,
    AccountNotActivatedError,
    InvalidCredentialsError,
    PasswordNotCompliantError,
    UserNotFoundError,
)
from carry_on.domain.repositories.user_repository import UserRepository
from carry_on.domain.security.password_hasher import PasswordHasher
from carry_on.services.authentication_service import (
    AuthenticatedUser,
    AuthenticationService,
    EmailCheckResult,
    LoginResult,
)


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create a mock UserRepository."""
    return MagicMock(spec=UserRepository)


@pytest.fixture
def mock_hasher() -> MagicMock:
    """Create a mock PasswordHasher."""
    hasher = MagicMock(spec=PasswordHasher)
    hasher.is_compliant.return_value = True
    hasher.verify.return_value = True
    hasher.needs_rehash.return_value = False
    hasher.hash.return_value = "$argon2id$hashed"
    return hasher


@pytest.fixture
def service(
    mock_repository: MagicMock, mock_hasher: MagicMock
) -> AuthenticationService:
    """Create an AuthenticationService with mocks."""
    return AuthenticationService(mock_repository, mock_hasher)


@pytest.fixture
def pending_user() -> User:
    """Create a user pending activation."""
    return User(
        id=UserId(value="user123"),
        email="test@example.com",
        display_name="Test User",
        password_hash=None,
        activated_at=None,
    )


@pytest.fixture
def activated_user() -> User:
    """Create an activated user."""
    return User(
        id=UserId(value="user123"),
        email="test@example.com",
        display_name="Test User",
        password_hash="$argon2id$hashed",
        activated_at=datetime(2026, 1, 25, 10, 0, 0, tzinfo=UTC),
    )


@allure.feature("Application Services")
@allure.story("Authentication Service")
class TestAuthenticationServiceInit:
    """Tests for AuthenticationService initialization."""

    def test_init_accepts_repository_and_hasher(
        self, mock_repository: MagicMock, mock_hasher: MagicMock
    ) -> None:
        """AuthenticationService should accept a repository and hasher."""
        service = AuthenticationService(mock_repository, mock_hasher)
        assert service._repository is mock_repository
        assert service._hasher is mock_hasher


@allure.feature("Application Services")
@allure.story("Authentication Service")
class TestCheckEmail:
    """Tests for AuthenticationService.check_email() method."""

    def test_check_email_returns_not_found_when_user_missing(
        self, service: AuthenticationService, mock_repository: MagicMock
    ) -> None:
        """Should raise UserNotFoundError when email doesn't exist."""
        mock_repository.find_by_email.return_value = None

        with pytest.raises(UserNotFoundError):
            service.check_email("unknown@example.com")

    def test_check_email_returns_needs_activation_for_pending_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        pending_user: User,
    ) -> None:
        """Should return needs_activation status for pending user."""
        mock_repository.find_by_email.return_value = pending_user

        result = service.check_email("test@example.com")

        assert isinstance(result, EmailCheckResult)
        assert result.status == "needs_activation"
        assert result.display_name == "Test User"

    def test_check_email_returns_activated_for_activated_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        activated_user: User,
    ) -> None:
        """Should return activated status for activated user."""
        mock_repository.find_by_email.return_value = activated_user

        result = service.check_email("test@example.com")

        assert result.status == "activated"
        assert result.display_name == "Test User"

    def test_check_email_normalizes_to_lowercase(
        self, service: AuthenticationService, mock_repository: MagicMock
    ) -> None:
        """Should normalize email to lowercase."""
        mock_repository.find_by_email.return_value = None

        with pytest.raises(UserNotFoundError):
            service.check_email("TEST@EXAMPLE.COM")

        mock_repository.find_by_email.assert_called_once_with("test@example.com")


@allure.feature("Application Services")
@allure.story("Authentication Service")
class TestActivateAccount:
    """Tests for AuthenticationService.activate_account() method."""

    def test_activate_raises_not_found_when_user_missing(
        self, service: AuthenticationService, mock_repository: MagicMock
    ) -> None:
        """Should raise UserNotFoundError when email doesn't exist."""
        mock_repository.find_by_email.return_value = None

        with pytest.raises(UserNotFoundError):
            service.activate_account("unknown@example.com", "password123")

    def test_activate_raises_already_activated_for_active_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        activated_user: User,
    ) -> None:
        """Should raise AccountAlreadyActivatedError for activated user."""
        mock_repository.find_by_email.return_value = activated_user

        with pytest.raises(AccountAlreadyActivatedError):
            service.activate_account("test@example.com", "password123")

    def test_activate_hashes_password_and_saves_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        pending_user: User,
    ) -> None:
        """Should hash password and save activated user."""
        mock_repository.find_by_email.return_value = pending_user
        mock_hasher.hash.return_value = "$argon2id$newhash"

        service.activate_account("test@example.com", "SecurePass1")

        mock_hasher.hash.assert_called_once_with("SecurePass1")
        mock_repository.save.assert_called_once()
        saved_user = mock_repository.save.call_args[0][0]
        assert saved_user.password_hash == "$argon2id$newhash"
        assert saved_user.is_activated

    def test_activate_returns_authenticated_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        pending_user: User,
    ) -> None:
        """Should return AuthenticatedUser on successful activation."""
        mock_repository.find_by_email.return_value = pending_user

        result = service.activate_account("test@example.com", "SecurePass1")

        assert isinstance(result, AuthenticatedUser)
        assert result.id == "user123"
        assert result.email == "test@example.com"
        assert result.display_name == "Test User"


@allure.feature("Application Services")
@allure.story("Authentication Service")
class TestLogin:
    """Tests for AuthenticationService.login() method."""

    def test_login_raises_invalid_credentials_when_user_missing(
        self, service: AuthenticationService, mock_repository: MagicMock
    ) -> None:
        """Should raise InvalidCredentialsError when email doesn't exist."""
        mock_repository.find_by_email.return_value = None

        with pytest.raises(InvalidCredentialsError):
            service.login("unknown@example.com", "password123")

    def test_login_raises_not_activated_for_pending_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        pending_user: User,
    ) -> None:
        """Should raise AccountNotActivatedError for pending user."""
        mock_repository.find_by_email.return_value = pending_user

        with pytest.raises(AccountNotActivatedError):
            service.login("test@example.com", "password123")

    def test_login_raises_invalid_credentials_for_wrong_password(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should raise InvalidCredentialsError for wrong password."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.verify.return_value = False

        with pytest.raises(InvalidCredentialsError):
            service.login("test@example.com", "wrongpassword")

    def test_login_triggers_rehash_when_needed(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should rehash password when algorithm is outdated."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.needs_rehash.return_value = True
        mock_hasher.hash.return_value = "$argon2id$newhash"

        service.login("test@example.com", "password123")

        mock_hasher.hash.assert_called_once_with("password123")
        mock_repository.save.assert_called_once()

    def test_login_returns_password_update_required_for_weak_password(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should return password_update_required for non-compliant password."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.is_compliant.return_value = False

        result = service.login("test@example.com", "1234")

        assert isinstance(result, LoginResult)
        assert result.status == "password_update_required"
        assert result.user.email == "test@example.com"

    def test_login_returns_success_for_valid_credentials(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        activated_user: User,
    ) -> None:
        """Should return success for valid credentials."""
        mock_repository.find_by_email.return_value = activated_user

        result = service.login("test@example.com", "SecurePass1")

        assert result.status == "success"
        assert result.user.email == "test@example.com"
        assert result.user.display_name == "Test User"


@allure.feature("Application Services")
@allure.story("Authentication Service")
class TestUpdatePassword:
    """Tests for AuthenticationService.update_password() method."""

    def test_update_password_raises_not_found_when_user_missing(
        self, service: AuthenticationService, mock_repository: MagicMock
    ) -> None:
        """Should raise UserNotFoundError when email doesn't exist."""
        mock_repository.find_by_email.return_value = None

        with pytest.raises(UserNotFoundError):
            service.update_password("unknown@example.com", "current", "newpassword")

    def test_update_password_raises_invalid_credentials_for_wrong_password(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should raise InvalidCredentialsError for wrong current password."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.verify.return_value = False

        with pytest.raises(InvalidCredentialsError):
            service.update_password("test@example.com", "wrong", "newpassword")

    def test_update_password_raises_not_compliant_for_weak_password(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should raise PasswordNotCompliantError for weak new password."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.is_compliant.return_value = False

        with pytest.raises(PasswordNotCompliantError):
            service.update_password("test@example.com", "current", "weak")

    def test_update_password_hashes_and_saves_new_password(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should hash new password and save user."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.hash.return_value = "$argon2id$newhash"

        service.update_password("test@example.com", "current", "NewSecurePass1")

        mock_hasher.hash.assert_called_once_with("NewSecurePass1")
        mock_repository.save.assert_called_once()
        saved_user = mock_repository.save.call_args[0][0]
        assert saved_user.password_hash == "$argon2id$newhash"


@allure.feature("Application Services")
@allure.story("Authentication Service")
class TestAuthenticate:
    """Tests for AuthenticationService.authenticate() method (header auth)."""

    def test_authenticate_raises_invalid_credentials_when_user_missing(
        self, service: AuthenticationService, mock_repository: MagicMock
    ) -> None:
        """Should raise InvalidCredentialsError when email doesn't exist."""
        mock_repository.find_by_email.return_value = None

        with pytest.raises(InvalidCredentialsError):
            service.authenticate("unknown@example.com", "password123")

    def test_authenticate_raises_invalid_credentials_for_wrong_password(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should raise InvalidCredentialsError for wrong password."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.verify.return_value = False

        with pytest.raises(InvalidCredentialsError):
            service.authenticate("test@example.com", "wrongpassword")

    def test_authenticate_triggers_rehash_when_needed(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        mock_hasher: MagicMock,
        activated_user: User,
    ) -> None:
        """Should rehash password when algorithm is outdated."""
        mock_repository.find_by_email.return_value = activated_user
        mock_hasher.needs_rehash.return_value = True
        mock_hasher.hash.return_value = "$argon2id$newhash"

        service.authenticate("test@example.com", "password123")

        mock_hasher.hash.assert_called_once_with("password123")
        mock_repository.save.assert_called_once()

    def test_authenticate_returns_authenticated_user(
        self,
        service: AuthenticationService,
        mock_repository: MagicMock,
        activated_user: User,
    ) -> None:
        """Should return AuthenticatedUser on success."""
        mock_repository.find_by_email.return_value = activated_user

        result = service.authenticate("test@example.com", "password123")

        assert isinstance(result, AuthenticatedUser)
        assert result.id == "user123"
        assert result.email == "test@example.com"
        assert result.display_name == "Test User"
