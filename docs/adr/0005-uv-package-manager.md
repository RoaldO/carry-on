# ADR 0005: uv for Dependency and Virtual Environment Management

## Status

Accepted

## Context

Python projects require tools for dependency management and virtual environment handling. Traditional options include pip + venv, Poetry, Pipenv, and PDM. We need a fast, reliable solution that works well with modern Python packaging standards.

## Decision

We will use **uv** for both dependency management and virtual environment management.

### Why uv over alternatives:

| Feature | uv | pip + venv | Poetry | PDM |
|---------|-----|------------|--------|-----|
| Speed | Extremely fast | Slow | Moderate | Fast |
| Written in | Rust | Python | Python | Python |
| Lock file | Yes (uv.lock) | No | Yes | Yes |
| PEP 621 (pyproject.toml) | Yes | Partial | Custom | Yes |
| Virtual env management | Built-in | Separate | Built-in | Built-in |
| Dependency groups | Yes | No | Yes | Yes |

### Configuration

All configuration lives in `pyproject.toml`:

```toml
[project]
name = "carry-on"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "pymongo>=4.10.0",
    "python-dotenv>=1.0.0",
    "uvicorn>=0.32.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]
```

### Common commands

```bash
# Create virtual environment and install dependencies
uv sync

# Install with dev dependencies
uv sync --dev

# Add a dependency
uv add requests

# Add a dev dependency
uv add --dev pytest-cov

# Run a command in the virtual environment
uv run pytest
uv run uvicorn api.index:app

# Export to requirements.txt (for Vercel deployment)
uv export --no-hashes > requirements.txt
```

### Virtual environment

uv automatically creates and manages `.venv/` in the project root:
- Created on first `uv sync`
- Activated automatically with `uv run`
- No manual activation needed

### Lock file

`uv.lock` ensures reproducible builds:
- Committed to git for reproducibility
- Contains exact versions of all transitive dependencies
- Cross-platform compatible

## Consequences

### Positive

- 10-100x faster than pip for dependency resolution
- Single tool replaces pip, venv, pip-tools
- Standards-compliant (PEP 621)
- Seamless virtual environment handling
- Lock file ensures reproducible builds

### Negative

- Relatively new tool (less battle-tested than pip)
- Requires uv to be installed on development machines
- Some CI environments may not have uv pre-installed

## References

- [uv documentation](https://docs.astral.sh/uv/)
- [PEP 621 - Project metadata](https://peps.python.org/pep-0621/)
- [Astral (uv creators)](https://astral.sh/)
