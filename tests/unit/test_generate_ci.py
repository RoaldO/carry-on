"""Tests for the CI workflow generator.

Tests that scripts/generate_ci.py correctly parses noxfile.py and
renders .github/workflows/ci.yml from the Jinja2 template.
"""

from pathlib import Path

import pytest

# The module under test lives at scripts/generate_ci.py.
# We import it via importlib so we don't need an __init__.py in scripts/.
import importlib.util

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
_spec = importlib.util.spec_from_file_location(
    "generate_ci", _SCRIPTS_DIR / "generate_ci.py"
)
assert _spec is not None and _spec.loader is not None
generate_ci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate_ci)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOXFILE = PROJECT_ROOT / "noxfile.py"


# ---------------------------------------------------------------------------
# AST parsing
# ---------------------------------------------------------------------------


class TestParseFinalRequires:
    """parse_final_requires() extracts the requires list from noxfile.py."""

    def test_extracts_sessions_from_noxfile(self) -> None:
        source = NOXFILE.read_text()
        result = generate_ci.parse_final_requires(source)
        assert isinstance(result, list)
        assert "lint" in result
        assert "typecheck" in result

    def test_includes_outdated_direct(self) -> None:
        source = NOXFILE.read_text()
        result = generate_ci.parse_final_requires(source)
        assert "outdated_direct" in result

    def test_includes_format(self) -> None:
        source = NOXFILE.read_text()
        result = generate_ci.parse_final_requires(source)
        assert "format" in result

    def test_minimal_noxfile(self) -> None:
        source = """
import nox

@nox.session(requires=["lint", "typecheck"])
def final(session):
    pass
"""
        result = generate_ci.parse_final_requires(source)
        assert result == ["lint", "typecheck"]

    def test_raises_if_no_final_session(self) -> None:
        source = """
import nox

@nox.session
def lint(session):
    pass
"""
        with pytest.raises(ValueError, match="final"):
            generate_ci.parse_final_requires(source)


class TestParsePythonVersion:
    """parse_python_version() extracts the Python version from noxfile.py."""

    def test_extracts_version(self) -> None:
        source = NOXFILE.read_text()
        result = generate_ci.parse_python_version(source)
        assert result == "3.14"

    def test_minimal_noxfile(self) -> None:
        source = """
import nox

@nox.session(python="3.12")
def lint(session):
    pass
"""
        result = generate_ci.parse_python_version(source)
        assert result == "3.12"


# ---------------------------------------------------------------------------
# Session mapping
# ---------------------------------------------------------------------------


class TestBuildLintSessions:
    """build_lint_sessions() maps final.requires to CI lint steps."""

    def test_format_becomes_format_check(self) -> None:
        requires = ["format", "lint", "typecheck"]
        result = generate_ci.build_lint_sessions(requires)
        session_names = [s["session"] for s in result]
        assert "format_check" in session_names
        assert "format" not in session_names

    def test_tests_excluded(self) -> None:
        requires = ["lint", "tests", "typecheck"]
        result = generate_ci.build_lint_sessions(requires)
        session_names = [s["session"] for s in result]
        assert "tests" not in session_names

    def test_preserves_order(self) -> None:
        requires = ["outdated_direct", "format", "lint", "typecheck"]
        result = generate_ci.build_lint_sessions(requires)
        session_names = [s["session"] for s in result]
        assert session_names.index("outdated_direct") < session_names.index("lint")

    def test_display_names(self) -> None:
        requires = ["lint", "format", "typecheck"]
        result = generate_ci.build_lint_sessions(requires)
        names_by_session = {s["session"]: s["name"] for s in result}
        assert names_by_session["lint"] == "Run linter"
        assert names_by_session["format_check"] == "Check formatting"
        assert names_by_session["typecheck"] == "Type check"

    def test_unknown_session_gets_default_name(self) -> None:
        requires = ["some_new_check"]
        result = generate_ci.build_lint_sessions(requires)
        assert result[0]["name"] == "some_new_check"
        assert result[0]["session"] == "some_new_check"


# ---------------------------------------------------------------------------
# Context building
# ---------------------------------------------------------------------------


class TestBuildContext:
    """build_context() combines parsed data into a template context."""

    def test_context_has_required_keys(self) -> None:
        ctx = generate_ci.build_context(NOXFILE.read_text())
        assert "python_version" in ctx
        assert "lint_sessions" in ctx

    def test_context_lint_sessions_is_list(self) -> None:
        ctx = generate_ci.build_context(NOXFILE.read_text())
        assert isinstance(ctx["lint_sessions"], list)
        assert len(ctx["lint_sessions"]) > 0

    def test_context_python_version(self) -> None:
        ctx = generate_ci.build_context(NOXFILE.read_text())
        assert ctx["python_version"] == "3.14"


# ---------------------------------------------------------------------------
# Round-trip: rendered template matches committed ci.yml
# ---------------------------------------------------------------------------


class TestRoundTrip:
    """Rendered template must match the committed ci.yml."""

    def test_rendered_matches_committed(self) -> None:
        ci_yml = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        rendered = generate_ci.render(
            noxfile_source=NOXFILE.read_text(),
            template_path=PROJECT_ROOT / ".github" / "workflows" / "ci.yml.j2",
        )
        assert rendered == ci_yml.read_text(), (
            "Rendered ci.yml does not match committed ci.yml. "
            "Run `uv run nox -s generate_ci` to regenerate."
        )
