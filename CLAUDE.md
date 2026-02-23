# CarryOn Project Instructions

## Architecture Decision Records

All development on this project MUST adhere to the Architecture Decision Records (ADRs).

See the full index at [`docs/adr/README.md`](docs/adr/README.md).

Read the ADRs before making changes to understand the rationale and implementation details.

## Architecture Enforcement (Deply)

This project uses [Deply](https://github.com/Vashkatsi/deply) to enforce layer boundaries (see `deply.yaml`). CI runs `deply analyze` and fails on violations.

**Deply performs bare-name matching**, not just import checks. If a variable or parameter name in one layer matches a class attribute or field name in a disallowed layer, Deply flags it as a dependency violation. This means:

- **Domain layer code must not use bare names that collide with API layer element names.** For example, Pydantic model fields in `carry_on/api/` like `strokes`, `course_name`, `hole_number` are registered as API elements. Using those exact names as function parameters or local variables in `carry_on/domain/` will trigger a `name_load` violation.
- **When naming parameters or variables in the domain layer**, use more specific names to avoid collisions (e.g., `gross_strokes` instead of `strokes`).
- Attribute access (e.g., `hole.strokes`) is fine — only bare name loads are checked.

Run the check locally with:

```bash
uv run --with deply deply analyze
```

## Testing

See the [Testing Guide](docs/testing.md) for how to run tests.

Always run tests before considering a task complete:

```bash
uv run pytest -v
```
