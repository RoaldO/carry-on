"""Nox sessions for CarryOn project.

Run `nox --list` to see available sessions.
Run `nox -s <session>` to run a specific session.
"""

import contextlib
import os

import nox
import subprocess
import re
import tomllib


# Use uv for all package management
nox.options.default_venv_backend = "uv"


@contextlib.contextmanager
def mongodb(session: nox.Session):
    container = "nox-mongo-test"
    image = "mongo:latest"
    username = "admin"
    password = "password"
    port = "27017"

    # Clean up any existing container from previous interrupted runs
    print(f"Cleaning up any existing {container=}")
    session.run("docker", "stop", container, external=True, success_codes=[0, 1])
    session.run("docker", "rm", container, external=True, success_codes=[0, 1])

    print(f"Starting {container=}")
    session.run(
        "docker",
        "run",
        "-d",
        "--name",
        container,
        "-p",
        f"{port}:27017",
        "-e",
        f"MONGO_INITDB_ROOT_USERNAME={username}",
        "-e",
        f"MONGO_INITDB_ROOT_PASSWORD={password}",
        image,
        external=True,
    )
    os.environ["MONGODB_URI"] = f"mongodb://{username}:{password}@localhost:{port}"

    try:
        yield
    finally:
        os.environ["MONGODB_URI"] = ""
        print(f"Cleaning up {container=}")
        session.run("docker", "stop", container, external=True)
        session.run("docker", "rm", container, external=True)


@nox.session(
    requires=[
        "outdated_direct",
        "format",
        "lint",
        "typecheck",
        "tests",
        "arch",
        "security",
        "secrets",
        "check_ci",
    ]
)
def final(session: nox.Session):
    """Final checks before pull request."""


@nox.session(python="3.14")
def security(session: nox.Session) -> None:
    """Scan dependencies for known security vulnerabilities."""
    session.install("pip-audit")
    session.run("pip-audit", *session.posargs)


@nox.session(python="3.14")
def secrets(session: nox.Session) -> None:
    """Scan for secrets in the codebase."""
    session.install("detect-secrets")
    session.run(
        "detect-secrets",
        "scan",
        "--baseline",
        ".secrets.baseline",
        *session.posargs,
    )


@nox.session
def arch(session):
    """Perform architecture validation of the project."""
    session.install("deply")
    session.run("deply", "analyze")


@nox.session(python="3.14")
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.install(".", "--group", "dev")

    # Prevent stale .pyc files from masking moved/deleted modules
    session.run(
        "python",
        "-Bc",
        "import pathlib, shutil;"
        " [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]",
    )

    with mongodb(session):
        session.run(
            "pytest",
            "-v",
            "--cov-report=term-missing",
            "--cov-report=html",
            *session.posargs,
        )


@nox.session(python="3.14")
def tests_acceptance(session: nox.Session) -> None:
    """Run only acceptance tests."""
    session.install(".", "--group", "dev")
    session.run("playwright", "install", "chromium", "--with-deps")
    with mongodb(session):
        session.run(
            "pytest",
            "-v",
            *(session.posargs or ["tests/acceptance/"]),
        )


@nox.session(python="3.14")
def tests_acceptance_headed(session: nox.Session) -> None:
    """Run only acceptance tests with browser visible."""
    session.install(".", "--group", "dev")
    session.run("playwright", "install", "chromium", "--with-deps")
    with mongodb(session):
        session.run(
            "pytest",
            "--headed",
            "-v",
            *(session.posargs or ["tests/acceptance/"]),
        )


@nox.session(python="3.14")
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


@nox.session(python="3.14")
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


@nox.session(python="3.14")
def lint(session: nox.Session) -> None:
    """Run ruff linter."""
    session.install("ruff==0.9.6")
    session.run("ruff", "check", "src/carry_on", "tests", *session.posargs)


@nox.session(python="3.14")
def format(session: nox.Session) -> None:
    """Run ruff formatter."""
    session.install("ruff==0.9.6")
    session.run("ruff", "format", "src/carry_on", "tests", *session.posargs)


@nox.session(python="3.14")
def format_check(session: nox.Session) -> None:
    """Check code formatting without making changes."""
    session.install("ruff==0.9.6")
    session.run("ruff", "format", "--check", "src/carry_on", "tests")


@nox.session(python="3.14")
def typecheck(session: nox.Session) -> None:
    """Run mypy type checker."""
    session.install(".", "--group", "dev")
    session.install("mypy", "types-requests")
    session.run("mypy", "src/carry_on", *session.posargs)


@nox.session(python="3.14")
def dev(session: nox.Session) -> None:
    """Run the development server."""
    session.install(".", "--group", "dev")
    session.run("uvicorn", "carry_on.api.index:app", "--port", "8787", "--reload")


@nox.session(python="3.14")
def generate_ci(session: nox.Session) -> None:
    """Regenerate .github/workflows/ci.yml from the Jinja2 template."""
    session.install("jinja2")
    session.run("python", "scripts/generate_ci.py", *session.posargs)


@nox.session(python="3.14")
def check_ci(session: nox.Session) -> None:
    """Check that ci.yml matches the Jinja2 template (drift detection)."""
    session.install("jinja2")
    session.run("python", "scripts/generate_ci.py", "--check", *session.posargs)


@nox.session(python="3.14")
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


@nox.session(python="3.14")
def profile(session: nox.Session) -> None:
    """Profile test execution and display performance report.

    Usage:
        nox -s profile -- tests/acceptance/path/to/test.py::test_name
        nox -s profile -- tests/unit/test_something.py
        nox -s profile    # profiles all tests (slow!)

    The session will:
    - Start MongoDB if needed
    - Run tests with cProfile
    - Generate and display profiling statistics

    Examples:
        # Profile a specific slow test
        nox -s profile -- \\
            tests/acceptance/step_defs/rounds/test_register_round.py::test_view_recent_rounds_history

        # Profile all acceptance tests
        nox -s profile -- tests/acceptance/
    """
    import tempfile

    session.install(".", "--group", "dev")

    # Check if we need Playwright (for acceptance tests)
    test_path = session.posargs[0] if session.posargs else "tests"
    needs_playwright = "acceptance" in test_path

    if needs_playwright:
        session.run("playwright", "install", "chromium")
        session.log("Note: If Playwright fails, install system deps with:")
        session.log("  playwright install-deps chromium")

    # Create temporary file for profile output
    with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as tmp:
        profile_file = tmp.name

    session.log("Running tests with profiling enabled...")
    session.log(f"Profile data will be saved to: {profile_file}")

    try:
        with mongodb(session):
            # Run pytest with cProfile
            session.run(
                "python",
                "-m",
                "cProfile",
                "-o",
                profile_file,
                "-m",
                "pytest",
                "-v",
                "--no-cov",  # Disable coverage for cleaner profiling
                *(session.posargs or ["tests"]),
            )

        # Analyze and display the profile
        session.log("\n" + "=" * 80)
        session.log("PROFILING REPORT")
        session.log("=" * 80 + "\n")

        # Create analysis script inline
        analysis_script = f"""
import pstats
from pstats import SortKey

stats = pstats.Stats('{profile_file}')

print("=" * 80)
print("TOP 20 FUNCTIONS BY CUMULATIVE TIME")
print("=" * 80)
stats.sort_stats(SortKey.CUMULATIVE).print_stats(20)

print("\\n" + "=" * 80)
print("TOP 20 FUNCTIONS BY TOTAL TIME (self time)")
print("=" * 80)
stats.sort_stats(SortKey.TIME).print_stats(20)

print("\\n" + "=" * 80)
print("APPLICATION CODE (carry_on and tests modules)")
print("=" * 80)
stats.sort_stats(SortKey.CUMULATIVE).print_stats('carry_on|tests', 30)
"""

        session.run("python", "-c", analysis_script)

        session.log("\n" + "=" * 80)
        session.log(f"Full profile data saved to: {profile_file}")
        session.log("You can analyze it further with pstats or visualization tools")
        session.log("=" * 80)

    except Exception as e:
        session.error(f"Profiling failed: {e}")


@nox.session(python="3.14")
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

    session.error(f"{len(outdated_direct)} direct dependencies are outdated.")
