"""Nox sessions for CarryOn project.

Run `nox --list` to see available sessions.
Run `nox -s <session>` to run a specific session.
"""

import nox
import sys
import subprocess
import re
import tomllib


# Use uv for all package management
nox.options.default_venv_backend = "uv"


@nox.session(
    requires=['outdated_direct', 'format', 'lint', 'typecheck', 'tests']
)
def final(session: nox.Session):
    """Final checks before pull request."""


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.install(".", "--group", "dev")

    # todo create a context manager for the mongodb container
    container_name = "nox-mongo-test"
    image = "mongo:latest"
    session.run(
        "docker", "run", "-d",
        "--name", container_name,
        "-p", "27017:27017",
        "-e", "MONGO_INITDB_ROOT_USERNAME=admin",
        "-e", "MONGO_INITDB_ROOT_PASSWORD=password",
        image,
        external=True
    )
    try:
        session.run(
            "pytest",
            "-v",
            "--cov-report=term-missing",
            "--cov-report=html",
            *session.posargs,
        )
    finally:
        print(f"Cleaning up container: {container_name}")
        session.run("docker", "stop", container_name, external=True)
        session.run("docker", "rm", container_name, external=True)


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
    import os
    import shutil

    session.install(".", "--group", "dev")
    # Generate results if not present
    if not os.path.exists("allure-results"):
        session.run(
            "pytest",
            "-v",
            "--alluredir=allure-results",
        )
    # Copy categories configuration
    if os.path.exists("allure-categories.json"):
        shutil.copy("allure-categories.json", "allure-results/categories.json")
        session.log("Copied allure-categories.json to allure-results/")
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


@nox.session(python="3.12")
def outdated_all(session: nox.Session) -> None:
    """
    Show all outdated dependencies and where they come from
    using reverse dependency trees.
    """
    session.install("uv")

    # Get outdated packages
    result = subprocess.run(
        ["uv", "pip", "list", "--outdated"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        session.error(result.stderr)

    lines = result.stdout.strip().splitlines()
    if len(lines) <= 2:
        session.log("No outdated dependencies found ✅")
        return

    header, separator, *rows = lines

    session.log("Outdated dependencies and their origins:\n")

    for row in rows:
        pkg = row.split()[0]
        session.log(f"\n=== {pkg} ===")
        tree = subprocess.run(
            ["uv", "pip", "tree", "--reverse", "--package", pkg],
            capture_output=True,
            text=True,
        )
        if tree.returncode == 0:
            session.log(tree.stdout.rstrip())
        else:
            session.log("  (could not determine dependency tree)")

@nox.session(python="3.12")
def outdated_direct(session: nox.Session) -> None:
    """
    Show outdated *direct* dependencies from pyproject.toml.
    Fails the session if any are found.
    """
    session.install("uv")

    # --- parse direct deps from pyproject.toml ---

    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)

    deps = pyproject.get("project", {}).get("dependencies", [])
    if not deps:
        session.log("No direct dependencies found.")
        return

    def normalize(dep: str) -> str:
        # strip extras, version specifiers, markers
        name = re.split(r"[<>=!~ ;]", dep, 1)[0]
        return name.split("[", 1)[0].lower()

    direct_names = {normalize(d) for d in deps}

    # --- run uv pip list --outdated ---
    result = subprocess.run(
        ["uv", "pip", "list", "--outdated"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        session.error(result.stderr)

    lines = result.stdout.strip().splitlines()
    if len(lines) <= 2:
        session.log("No outdated dependencies found.")
        return

    header, separator, *rows = lines

    outdated_direct = []
    for row in rows:
        pkg = row.split()[0].lower()
        if pkg in direct_names:
            outdated_direct.append(row)

    if not outdated_direct:
        session.log("All direct dependencies are up to date ✅")
        return

    session.log("Outdated direct dependencies:")
    session.log(header)
    session.log(separator)
    for row in outdated_direct:
        session.log(row)

    session.error(
        f"{len(outdated_direct)} direct dependencies are outdated."
    )
