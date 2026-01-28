"""Nox sessions for CarryOn project.

Run `nox --list` to see available sessions.
Run `nox -s <session>` to run a specific session.
"""

import nox

# Use uv for all package management
nox.options.default_venv_backend = "uv"


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.install(".", "--group", "dev")
    session.run(
        "pytest",
        "-v",
        "--cov-report=term-missing",
        "--cov-report=html",
        *session.posargs,
    )


@nox.session(python="3.12")
def tests_fast(session: nox.Session) -> None:
    """Run tests without acceptance tests (faster)."""
    session.install(".", "--group", "dev")
    session.run(
        "pytest",
        "-v",
        "-m",
        "not acceptance",
        "--cov-report=term-missing",
        *session.posargs,
    )


@nox.session(python="3.12")
def tests_acceptance(session: nox.Session) -> None:
    """Run only acceptance tests."""
    session.install(".", "--group", "dev")
    session.run("playwright", "install", "chromium", "--with-deps")
    session.run(
        "pytest",
        "-v",
        "-m",
        "acceptance",
        *session.posargs,
    )


@nox.session(python="3.12")
def allure(session: nox.Session) -> None:
    """Generate Allure report from test results.

    Run tests first with: nox -s tests -- --alluredir=allure-results
    Then run: nox -s allure
    """
    session.install(".", "--group", "dev")
    # Generate results if not present
    import os
    if not os.path.exists("allure-results"):
        session.run(
            "pytest",
            "-v",
            "--alluredir=allure-results",
        )
    session.log("Allure results generated in allure-results/")
    session.log("To view the report, install Allure CLI and run:")
    session.log("  allure serve allure-results")


@nox.session(python="3.12")
def coverage_html(session: nox.Session) -> None:
    """Generate HTML coverage report."""
    session.install(".", "--group", "dev")
    session.run(
        "pytest",
        "-v",
        "--cov-report=html",
        *session.posargs,
    )
    session.log("Coverage report generated in htmlcov/")
    session.log("Open htmlcov/index.html in a browser to view.")


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    """Run ruff linter."""
    session.install("ruff")
    session.run("ruff", "check", "src/carry_on", "tests", *session.posargs)


@nox.session(python="3.12")
def format(session: nox.Session) -> None:
    """Run ruff formatter."""
    session.install("ruff")
    session.run("ruff", "format", "src/carry_on", "tests", *session.posargs)


@nox.session(python="3.12")
def format_check(session: nox.Session) -> None:
    """Check code formatting without making changes."""
    session.install("ruff")
    session.run("ruff", "format", "--check", "src/carry_on", "tests")


@nox.session(python="3.12")
def typecheck(session: nox.Session) -> None:
    """Run mypy type checker."""
    session.install(".", "--group", "dev")
    session.install("mypy", "types-requests")
    session.run("mypy", "src/carry_on", *session.posargs)


@nox.session(python="3.12")
def dev(session: nox.Session) -> None:
    """Run the development server."""
    session.install(".", "--group", "dev")
    session.run("uvicorn", "carry_on.api.index:app", "--port", "8787", "--reload")
