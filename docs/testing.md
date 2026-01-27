# Testing Guide

This project uses pytest as its testing framework, following [ADR-0004](adr/0004-pytest.md).

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures for unit/integration tests
├── acceptance/                    # BDD acceptance tests
│   ├── conftest.py               # Server and Playwright fixtures
│   ├── features/                 # Gherkin feature files
│   │   └── auth/
│   │       ├── registration.feature
│   │       └── login.feature
│   ├── step_defs/                # Step definitions
│   │   ├── test_registration.py
│   │   └── test_login.py
│   └── pages/                    # Page Object Models
│       └── login_page.py
├── domain/                       # Domain layer tests
├── infrastructure/               # Infrastructure layer tests
├── services/                     # Service layer tests
└── test_*.py                     # API integration tests
```

## Running Tests

### All Tests

```bash
uv run pytest -v
```

### Unit and Integration Tests Only

```bash
uv run pytest -v -m "not acceptance"
```

### Acceptance Tests Only

```bash
uv run pytest tests/acceptance/ -v
```

### With Visible Browser (Debugging)

```bash
uv run pytest tests/acceptance/ -v --headed
```

### Specific Test File

```bash
uv run pytest tests/test_api.py -v
```

### Specific Test

```bash
uv run pytest tests/test_api.py::TestStrokesEndpoint::test_post_stroke_with_valid_auth -v
```

## Test Types

### Unit Tests

Located in `tests/domain/` and `tests/services/`. These test individual components in isolation with mocked dependencies.

### Integration Tests

Located in `tests/test_*.py`. These test API endpoints using FastAPI's TestClient with mocked MongoDB collections.

### Acceptance Tests

Located in `tests/acceptance/`. These are BDD-style tests using:

- **pytest-bdd**: For Gherkin feature files and step definitions
- **Playwright**: For browser automation

Acceptance tests run against a real HTTP server (uvicorn in a background thread) with mocked MongoDB, allowing full end-to-end testing of the UI.

#### Writing Feature Files

Feature files use Gherkin syntax and are located in `tests/acceptance/features/`:

```gherkin
Feature: User Login
  As a registered user
  I want to log in with my email and PIN
  So that I can access my golf stroke data

  Scenario: User logs in with valid credentials
    Given I am on the login screen
    And a user exists with email "test@example.com" and PIN "1234"
    When I enter email "test@example.com"
    And I click the continue button
    And I enter PIN "1234"
    And I click the submit button
    Then I should be logged in
```

#### Writing Step Definitions

Step definitions map Gherkin steps to Python code:

```python
from pytest_bdd import given, when, then, parsers, scenarios

scenarios("../features/auth/login.feature")

@given("I am on the login screen")
def on_login_screen(login_page):
    login_page.goto_login()

@when(parsers.parse('I enter email "{email}"'))
def enter_email(login_page, email):
    login_page.enter_email(email)
```

#### Page Object Model

Page objects encapsulate page interactions in `tests/acceptance/pages/`:

```python
class LoginPage:
    def __init__(self, page, base_url):
        self.page = page
        self.email_input = page.locator("#email")

    def enter_email(self, email):
        self.email_input.fill(email)
```

## Coverage

Tests include coverage reporting. The project requires a minimum of 70% coverage:

```bash
# Run with coverage (default)
uv run pytest -v

# Run without coverage
uv run pytest -v --no-cov
```

## First-Time Setup

Before running acceptance tests for the first time, install Playwright browsers:

```bash
uv run playwright install chromium
```
