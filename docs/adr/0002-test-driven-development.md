# ADR 0002: Test-Driven Development

## Status

Accepted

## Context

As CarryOn grows in complexity with features like Stableford scoring, handicap calculations, and round tracking, we need confidence that changes don't break existing functionality. We also want to ensure the domain logic is correct from the start.

## Decision

We will use Test-Driven Development (TDD) as our primary development methodology.

### The TDD cycle we follow:

1. **Red**: Write a failing test that describes the desired behavior
2. **Green**: Write the minimum code to make the test pass
3. **Refactor**: Improve the code while keeping tests green

### Testing strategy:

1. **Unit Tests**: Test domain models and business logic in isolation
   - Stableford point calculations
   - Handicap calculations
   - Shot distance statistics

2. **Integration Tests**: Test API endpoints with mocked database
   - Authentication (PIN verification)
   - CRUD operations for shots, rounds, courses

3. **End-to-End Tests** (future): Test complete user flows
   - Recording a full round
   - Viewing statistics

### Tools:

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for API testing
- **unittest.mock**: Mocking MongoDB and external dependencies

### Commit workflow:

1. Commit the failing test first
2. Commit the implementation that makes it pass
3. Commit any refactoring separately

## Consequences

### Positive

- High test coverage from the start
- Tests serve as living documentation
- Confidence when refactoring
- Catches regressions early
- Forces thinking about API design before implementation

### Negative

- Slower initial development
- Tests need maintenance as requirements change
- Learning curve for TDD discipline

## References

- Kent Beck, "Test-Driven Development: By Example"
- [pytest documentation](https://docs.pytest.org/)
