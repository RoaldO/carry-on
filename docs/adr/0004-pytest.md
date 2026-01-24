# ADR 0004: pytest as Testing Framework

## Status

Accepted

## Context

We need a testing framework for our TDD approach (see ADR-0002). Python offers several options including unittest (stdlib), pytest, and nose2.

## Decision

We will use **pytest** as our testing framework.

### Why pytest over alternatives:

| Feature | pytest | unittest | nose2 |
|---------|--------|----------|-------|
| Simple assert statements | Yes | No (self.assertEqual) | Yes |
| Fixtures | Powerful | setUp/tearDown only | Limited |
| Parametrization | Built-in | No | Plugin |
| Plugin ecosystem | Extensive | Limited | Moderate |
| Async support | pytest-asyncio | asyncio.TestCase | Limited |

### Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### Dependencies

```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]
```

### Project structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_api.py          # API endpoint tests
├── test_domain/         # Domain model tests
│   ├── test_shot.py
│   ├── test_round.py
│   └── test_stableford.py
└── test_repositories/   # Repository tests
    └── test_shot_repository.py
```

### Key features we use:

1. **Fixtures** (`conftest.py`): Reusable test setup
   ```python
   @pytest.fixture
   def mock_shots_collection():
       ...
   ```

2. **Parametrization**: Test multiple inputs
   ```python
   @pytest.mark.parametrize("club,expected", [("i7", 150), ("d", 220)])
   def test_average_distance(club, expected):
       ...
   ```

3. **Markers**: Categorize tests
   ```python
   @pytest.mark.integration
   def test_database_connection():
       ...
   ```

### Running tests

```bash
uv run pytest              # Run all tests
uv run pytest -v           # Verbose output
uv run pytest -k "shot"    # Run tests matching "shot"
uv run pytest --cov        # With coverage (requires pytest-cov)
```

## Consequences

### Positive

- Clean, readable test code with simple asserts
- Powerful fixture system for DRY test setup
- Excellent FastAPI/async support via plugins
- Rich plugin ecosystem for coverage, mocking, etc.
- Industry standard for Python projects

### Negative

- External dependency (not stdlib)
- Fixture magic can be confusing for newcomers
- Some implicit behavior requires learning

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
