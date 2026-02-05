# CarryOn

[![Coverage Report](https://img.shields.io/badge/coverage-report-blue)](https://roaldo.github.io/carry-on/coverage/)
[![Test Results](https://img.shields.io/badge/test%20results-allure-orange)](https://roaldo.github.io/carry-on/allure/)

Golf stroke tracking web application.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas
- **Hosting**: Vercel (serverless)
- **Package Manager**: uv

## Getting Started

```bash
# Install dependencies
uv sync --dev

# Set up pre-commit hooks (one-time setup)
uv run pre-commit install

# Run locally
uv run nox -s dev
```

## Development with Nox

This project uses [nox](https://nox.thea.codes/) for task automation. All sessions use uv for fast, consistent environments.

```bash
# List available sessions
uv run nox --list

# Run tests (full suite with coverage)
uv run nox -s tests

# Run tests without acceptance tests (faster)
uv run nox -s tests_fast

# Run only acceptance tests
uv run nox -s tests_acceptance

# Run linter
uv run nox -s lint

# Format code
uv run nox -s format

# Type checking
uv run nox -s typecheck

# Architecture validation
uv run nox -s arch

# Check for secrets and passwords
uv run nox -s secrets

# Check for unsafe packages
uv run nox -s security

# Run development server
uv run nox -s dev
```

## Testing

See the [Testing Guide](docs/testing.md) for detailed information on running tests, including unit tests, integration tests, and BDD acceptance tests with Playwright.

## Development Guidelines

All contributors MUST adhere to the Architecture Decision Records (ADRs).

See the full index at [`docs/adr/README.md`](docs/adr/README.md).

Please read these ADRs before contributing to understand our development practices and architectural decisions.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
