# ADR 0013: CI Workflow Generation from Noxfile

## Status

Accepted

## Context

The CI workflow (`.github/workflows/ci.yml`) and `noxfile.py` encode overlapping
information — which lint checks to run and what Python version to use. When a new
nox session is added to `final.requires`, someone must remember to also update
`ci.yml`. This has already drifted: the `outdated_direct` session is listed in
`final.requires` but missing from the CI workflow.

Keeping two sources of truth in sync manually is error-prone and violates the
DRY principle.

## Decision

We generate `.github/workflows/ci.yml` from `noxfile.py` using a Jinja2 template
and a Python generator script:

- **Template** at `.github/workflows/ci.yml.j2` — looks like the current CI
  workflow with placeholders for the dynamic parts (lint session list, Python
  version).
- **Generator** at `scripts/generate_ci.py` — parses `noxfile.py` via the `ast`
  module, extracts configuration (session list from `final.requires`, Python
  version), and renders the template.
- **Custom Jinja2 delimiters** (`[[ ]]` / `[% %]` / `[# #]`) avoid collision
  with GitHub Actions `${{ }}` expressions and bash heredocs (`<<`).
- **`--check` mode** compares the rendered output with the committed `ci.yml`
  and exits non-zero on drift.

### What is dynamic vs static

- **Dynamic**: lint job session list (derived from `final.requires`), Python
  version.
- **Static**: test job (MongoDB service, Playwright, Allure, artifacts, deploy).
  These are CI-specific infrastructure that don't map 1:1 to nox sessions.

### Session mapping

| `final.requires` | CI session | Reason |
|---|---|---|
| `format` | `format_check` | CI checks formatting, it does not reformat |
| `tests` | *(excluded)* | Test job has different needs (Allure, artifacts, Playwright) |
| all others | used as-is | Direct 1:1 mapping |

### Drift detection

- A `check_ci` nox session runs the generator in `--check` mode.
- `check_ci` is added to `final.requires` so drift is caught in the standard
  pre-PR pipeline.
- A pre-commit hook triggers `--check` when `noxfile.py` or `ci.yml.j2` change.

## Consequences

### Positive

- Single source of truth: adding a session to `final.requires` automatically
  updates CI on the next regeneration.
- Drift is detected by `nox -s final`, pre-commit, and CI itself.
- The template remains readable YAML — non-dynamic parts are literal.

### Negative

- Contributors must remember to run `nox -s generate_ci` after changing
  `noxfile.py` or the template. The pre-commit hook and `check_ci` session
  mitigate this by catching forgotten regeneration.
- Adding a new dependency (`jinja2`) for the generator.
