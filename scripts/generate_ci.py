"""Generate .github/workflows/ci.yml from noxfile.py and a Jinja2 template.

Usage:
    python scripts/generate_ci.py            # regenerate ci.yml
    python scripts/generate_ci.py --check    # check for drift (exit 1 if different)
"""

from __future__ import annotations

import ast
import difflib
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ── Session name mapping ─────────────────────────────────────────────────
# Keys in final.requires that need special treatment in CI.
SESSION_MAP: dict[str, str | None] = {
    "format": "format_check",  # CI checks formatting; it doesn't reformat
    "tests": None,  # test job is handled separately
}

# Human-readable display names for CI step labels.
DISPLAY_NAMES: dict[str, str] = {
    "lint": "Run linter",
    "format_check": "Check formatting",
    "typecheck": "Type check",
    "arch": "Architecture check",
    "security": "Security scan",
    "secrets": "Secrets scan",
    "outdated_direct": "Check outdated direct dependencies",
    "check_ci": "Verify CI workflow is up to date",
}


# ── AST helpers ──────────────────────────────────────────────────────────


def parse_final_requires(source: str) -> list[str]:
    """Extract the ``requires`` list from the ``final`` nox session decorator."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "final":
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            for kw in decorator.keywords:
                if kw.arg == "requires" and isinstance(kw.value, ast.List):
                    return [
                        elt.value
                        for elt in kw.value.elts
                        if isinstance(elt, ast.Constant)
                    ]
    msg = "Could not find a 'final' session with a 'requires' keyword in noxfile"
    raise ValueError(msg)


def parse_python_version(source: str) -> str:
    """Extract the Python version from the first ``@nox.session(python=...)``."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            for kw in decorator.keywords:
                if kw.arg == "python" and isinstance(kw.value, ast.Constant):
                    return str(kw.value.value)
    msg = "Could not find a python= keyword in any @nox.session decorator"
    raise ValueError(msg)


# ── Context building ─────────────────────────────────────────────────────


def build_lint_sessions(
    requires: list[str],
) -> list[dict[str, str]]:
    """Map ``final.requires`` entries to CI lint job steps.

    Returns a list of dicts with ``session`` (nox session name) and ``name``
    (human-readable step label).
    """
    sessions: list[dict[str, str]] = []
    for req in requires:
        mapped = SESSION_MAP.get(req, req)
        if mapped is None:
            continue  # explicitly excluded (e.g. tests)
        name = DISPLAY_NAMES.get(mapped, mapped)
        sessions.append({"session": mapped, "name": name})
    return sessions


def build_context(noxfile_source: str) -> dict[str, object]:
    """Build the full Jinja2 template context from noxfile source."""
    requires = parse_final_requires(noxfile_source)
    python_version = parse_python_version(noxfile_source)
    lint_sessions = build_lint_sessions(requires)
    return {
        "python_version": python_version,
        "lint_sessions": lint_sessions,
    }


# ── Rendering ────────────────────────────────────────────────────────────


def render(
    noxfile_source: str,
    template_path: Path,
) -> str:
    """Render the CI workflow from a Jinja2 template and noxfile source."""
    ctx = build_context(noxfile_source)
    env = Environment(  # noqa: S701 — generating YAML, not HTML
        loader=FileSystemLoader(str(template_path.parent)),
        variable_start_string="[[",
        variable_end_string="]]",
        block_start_string="[%",
        block_end_string="%]",
        comment_start_string="[#",
        comment_end_string="#]",
        keep_trailing_newline=True,
    )
    template = env.get_template(template_path.name)
    return template.render(**ctx)


# ── CLI ──────────────────────────────────────────────────────────────────


def main() -> None:
    noxfile_path = PROJECT_ROOT / "noxfile.py"
    template_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml.j2"
    ci_yml_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"

    noxfile_source = noxfile_path.read_text()
    rendered = render(noxfile_source, template_path)

    if "--check" in sys.argv:
        if not ci_yml_path.exists():
            print("ERROR: ci.yml does not exist. Run without --check first.")
            sys.exit(1)

        existing = ci_yml_path.read_text()
        if rendered == existing:
            print("ci.yml is up to date.")
            sys.exit(0)

        diff = difflib.unified_diff(
            existing.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile="ci.yml (committed)",
            tofile="ci.yml (rendered)",
        )
        sys.stdout.writelines(diff)
        print("\nERROR: ci.yml is out of date. Run `uv run nox -s generate_ci`.")
        sys.exit(1)

    ci_yml_path.write_text(rendered)
    print(f"Generated {ci_yml_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
