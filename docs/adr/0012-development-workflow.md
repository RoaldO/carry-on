# ADR 0012: Development Workflow

## Status

Accepted

## Context

A consistent development workflow helps in maintaining a distraction free
development cycle.

## Decision

1. Run `uv run nox -s outdated_direct` and `uv run nox -s outdated_all` to see
   if any of the packages can and should be updated. This must treated a
   regular development cycle.
2. Start by creating a branch for the oncoming code change.
3. Run `uv run nox -s tests` to verify that the environment is stable.
4. Make the required code changes using [TDD](0002-test-driven-development.md).
5. When the functionality implemented, make sure the code is stable for
   potential release by running `uv run nox -s final`.
6. Submit pull request.

## Consequences

### Positive

- Less time waste wondering if a particular problem is related to the local 
  development setup.
- Less retries in the pull request to make it stable.
- Faster development cycle in the long run.

### Negative

- It **looks** slower to make very small and fast fixes.
