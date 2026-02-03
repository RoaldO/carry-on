# CarryOn Roadmap

## Current Features
- Record golf strokes (club, distance, fail)
- View recent strokes
- Multi-user authentication (email + password)

## Planned Features

### 0. Test, Build & Deploy Tooling
- [x] Set up pytest for backend testing
- [x] Add API endpoint tests
- [x] CI/CD pipeline (GitHub Actions)
- [x] Automated deployment to Vercel on push
- [x] Add BDD acceptance tests with pytest-bdd and Playwright

### 0b. In-App Idea Capture
- [x] Submit new feature ideas/feedback from within the app
- [x] Store ideas in database for later review
- [x] Move "Submit an Idea" to a less intrusive location

### 0c. Refactor to DDD/SOLID (ADR Compliance)
Refactor codebase to follow ADR-0001 (DDD) and ADR-0003 (SOLID):
- [x] Create ubiquitous language glossary (`docs/glossary.md`)
- [x] Create domain layer with Stroke entity and value objects (ClubType, Distance)
- [x] Create repository layer (`domain/repositories/`, `infrastructure/repositories/`)
- [x] Create service layer (`services/stroke_service.py`) for business logic
- [x] Refactor POST /api/strokes to use StrokeService
- [x] Refactor GET /api/strokes to use StrokeService (requires created_at in domain)
- [x] Update tests to use dependency injection

### 0d. Dependency Version Audit (ADR-0007 Compliance)
- [x] Check all dependencies are on latest patch version
- [x] Upgrade to latest minor versions where available
- [x] Track uv.lock for reproducible builds

### 0e. Code Coverage
- [x] Add pytest-cov for coverage reporting
- [x] Add coverage check to CI pipeline
- [x] Set minimum coverage threshold (70%)

### 0f. Multi-User Support
Transition from single-user to multi-user before adding more features.
See [specification](docs/specs/multi-user.md) for details.
- [x] Write specification
- [x] Create users collection and User entity
- [x] Implement check-email endpoint (`POST /api/check-email`)
- [x] Implement activation endpoint (`POST /api/activate`)
- [x] Implement login endpoint (`POST /api/login`)
- [x] Update UI with email/password login flow
- [x] Remove legacy APP_PIN authentication
- [x] Secure password hashing with Argon2id (see [ADR-0009](docs/adr/0009-password-hashing.md))
- [x] Add user_id to strokes and ideas
- [x] Filter strokes/ideas by logged-in user
- [x] Migrate existing data to default user

### 0g. Password Complexity Support
Allow users to use generated passwords from password managers.
- [x] Rename "PIN" to "password" throughout codebase (API, UI, docs)
- [x] Rename `pin_hash` to `password_hash` in database schema
- [x] Increase minimum password length from 4 to 8 characters (for activation)
- [x] Remove 10 character limit on password field
- [x] Support special characters in password field (e.g., `!@#$%^&*`)
- [x] Support mixed case letters (uppercase and lowercase)
- [x] Support numbers
- [x] Update password field validation to accept complex passwords
- [x] Update UI input field to allow all character types
- [x] Add migration flow for users with weak passwords

### 0h. Tab Navigation
Implement tab-based navigation for better app structure.
See [specification](docs/specs/navigation.md) for details.
- [x] Add tab bar component (bottom of screen)
- [x] Create Strokes tab (current main page)
- [x] Create Ideas tab (merged into main page)
- [x] Highlight active tab
- [x] Hide tab bar on login/activation screens
- [x] URL hash routing (#strokes, #ideas)
- [x] Create Profile tab with user info and logout
- [x] Implement `/api/me` endpoint for profile data

### 0i. Acceptance Tests for Current Specifications
Add BDD acceptance tests covering all existing specifications.
See [ADR-0011](docs/adr/0011-specification-acceptance-tests.md) for testing approach.

**Multi-User (`docs/specs/multi-user.md`):**
- [x] Login feature (`tests/acceptance/features/auth/login.feature`)
- [x] Registration feature (`tests/acceptance/features/auth/registration.feature`)
- [x] Session persistence tests (`tests/acceptance/features/auth/session.feature`)
- [x] Logout tests (`tests/acceptance/features/navigation/profile.feature`)

**Stroke Tracking (`docs/specs/stroke-tracking.md`):**
- [x] Record successful stroke (`tests/acceptance/features/strokes/record.feature`)
- [ ] Record failed stroke
- [ ] View recent strokes
- [ ] Stroke validation (club, distance)

**Idea Capture (`docs/specs/idea-capture.md`):**
- [ ] Submit idea
- [ ] ~~View submitted ideas~~ (endpoint removed)
- [ ] Character limit validation

**Navigation (`docs/specs/navigation.md`):**
- [x] Tab switching between Strokes, Ideas, and Profile (`tests/acceptance/features/navigation/tabs.feature`)
- [x] URL hash routing (`tests/acceptance/features/navigation/tabs.feature`)
- [x] Tab bar visibility (hidden on login) (`tests/acceptance/features/navigation/tabs.feature`)
- [x] Profile display (`tests/acceptance/features/navigation/profile.feature`)

### 0j. Code Coverage Report
Generate detailed code coverage reports for visibility into test coverage.
- [x] Generate HTML coverage report locally (`uv run pytest --cov-report=html`)
- [x] Add coverage report to CI artifacts
- [x] Configure coverage report to exclude test files
- [x] Add coverage badge to README
- [x] Deploy coverage report to GitHub Pages (https://roaldo.github.io/carry-on/)

### 0k. Test Result Report
Generate detailed test result reports for visibility into test execution.
- [x] Evaluate reporting options (pytest-html, Allure, JUnit XML) → Chose Allure
- [x] Install and configure chosen reporting tool (allure-pytest)
- [x] Generate HTML test report locally
- [x] Add test report to CI artifacts
- [x] Include BDD scenario names in report output
- [x] Deploy test report to GitHub Pages (https://roaldo.github.io/carry-on/allure/)
- [x] Add build history support (test duration trends, pass/fail history per test)
- [x] Add custom categories for test failure classification
- [x] Add warnings log to GitHub Pages

### 0l. Convert unittest Style Tests to pytest
Modernize test suite by converting unittest-style tests to idiomatic pytest.
- [x] Replace `unittest.TestCase` classes with plain test functions
- [x] Replace `self.assert*` methods with plain `assert` statements
- [x] Replace `setUp`/`tearDown` with pytest fixtures
- [x] Use `@pytest.fixture` instead of `setUpClass`/`tearDownClass`
- [x] Use `@pytest.mark.parametrize` for data-driven tests
- [x] Remove unnecessary test class inheritance

### 0m. Allure Feature Decorators
Mark tests with Allure decorators for better test organization and reporting.
- [x] Install allure-pytest package
- [x] Add `@allure.feature()` decorators to group tests by feature
- [x] Add `@allure.story()` decorators for user stories within features
- [x] BDD tests automatically inherit feature names from .feature files

### 0o. Task Automation with Nox
Set up nox for consistent test running and other development tasks.
- [x] Install nox and nox-uv packages
- [x] Configure nox to use uv backend (`nox.options.default_venv_backend = "uv"`)
- [x] Add `tests` session (full test suite with coverage)
- [x] Add `tests_fast` session (skip acceptance tests)
- [x] Add `tests_acceptance` session (acceptance tests only)
- [x] Add `tests_acceptance_headed` session (acceptance tests with visible browser)
- [x] Add `lint` session (ruff check)
- [x] Add `format` session (ruff format)
- [x] Add `typecheck` session (mypy)
- [x] Add `dev` session (run development server)
- [x] Add `final` session (pre-MR checks: outdated, format, lint, typecheck, tests)
- [x] Add `outdated_direct` session (check direct dependencies)
- [x] Add `outdated_all` session (show all outdated dependencies)
- [x] Add `coverage_html` session (generate HTML coverage report)
- [x] Add `allure` session (generate Allure report)

### 0n. HTML Rendering Refactor
Remove duplication between `public/index.html` and inline HTML in `api/index.py`.
- [x] Audit differences between `public/index.html` and `get_inline_html()`
- [x] Decide on single source of truth (file vs inline)
- [x] Remove duplicate HTML code
- [x] Ensure Vercel deployment still works correctly
- [x] Add tests to verify HTML serving behavior

### 0p. CI Code Quality Checks
Add linting, formatting, and type checking to CI pipeline.
- [x] Add ruff lint check to CI (`nox -s lint`)
- [x] Add ruff format check to CI (`nox -s format_check`)
- [x] Add mypy type check to CI (`nox -s typecheck`)
- [x] Run quality checks before tests in pipeline

### 0q. Architecture Validation with Deply
Use deply to enforce architectural boundaries and dependency rules.
- [x] Install deply package
- [x] Configure layer definitions (domain, infrastructure, api, services)
- [x] Define dependency rules (e.g., domain must not depend on infrastructure)
- [x] Add `deply` nox session for architecture checks
- [ ] Add architecture validation to CI pipeline

### 0r. Infer GitHub Actions from Project Configuration
Generate CI workflow from noxfile.py to avoid duplication and drift.
- [ ] Evaluate approach (nox session to generate workflow, or template-based)
- [ ] Create script/session to generate `.github/workflows/ci.yml`
- [ ] Ensure generated workflow matches current CI behavior
- [ ] Document regeneration process

### 0s. Pre-commit Hooks
Catch issues before commit to prevent CI failures and keep commits clean.
- [ ] Install pre-commit package
- [ ] Create `.pre-commit-config.yaml` configuration
- [ ] Add ruff linting hook
- [ ] Add ruff formatting hook
- [ ] Add mypy type checking hook
- [ ] Document setup for new contributors (`pre-commit install`)

### 0t. Dependency Security Scanning
Scan dependencies for known security vulnerabilities.
- [ ] Install pip-audit package
- [ ] Add `security` nox session to run pip-audit
- [ ] Add security scan to CI pipeline
- [ ] Configure to fail on high/critical vulnerabilities

### 0u. Automated Dependency Updates
Automatically create PRs for dependency updates.
- [ ] Create `.github/dependabot.yml` configuration
- [ ] Configure update schedule (weekly)
- [ ] Configure Python ecosystem (pip/uv)
- [ ] Set PR limits and reviewers

### 0v. Secrets Detection
Prevent accidental commits of API keys, passwords, and other secrets.
- [ ] Install detect-secrets package
- [ ] Generate baseline file (`.secrets.baseline`)
- [ ] Add detect-secrets pre-commit hook
- [ ] Add secrets scan to CI pipeline

### 0w. Production Error Tracking
Track and monitor errors in production with Sentry.
- [ ] Create Sentry project for CarryOn
- [ ] Install sentry-sdk package
- [ ] Configure Sentry DSN in environment
- [ ] Initialize Sentry in FastAPI app
- [ ] Configure error filtering and sampling
- [ ] Add source maps for frontend errors (optional)

### 0x. Database Backup
Implement automated backup strategy for MongoDB Atlas to prevent data loss.
- [x] Implement a simplified backup and restore script.

### 1. Golf Course Management
Store golf course information including:
- Course name
- Number of holes (9/18)
- Par per hole
- Stroke index per hole (for handicap allocation)

### 2. Player Handicap
- Store player handicap index
- Support for course handicap calculation based on course rating/slope

### 3. Stableford Score Calculation
- Calculate Stableford points per hole based on:
  - Net strokes (gross - handicap strokes)
  - Par for the hole
- Show running Stableford total during round
- Store completed rounds with final scores

### 4. Round Tracking
Use the app during a round to:
- Select a course
- Track strokes per hole
- Tally total hits in real-time
- Mark penalties, putts, etc.
- Measure stroke distances (club + distance per stroke)

### 5. GPS & Club Advice
- Mark hole locations by GPS when on the course (tee, green/pin)
- Store GPS coordinates per hole for later reference
- Get current location during round
- Calculate distance to hole
- Recommend clubs based on historical stroke data (average distance per club)
