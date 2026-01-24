# ADR 0003: SOLID Principles

## Status

Accepted

## Context

To maintain a clean, extensible, and testable codebase as CarryOn grows, we need guiding principles for code design. SOLID principles provide a proven foundation for object-oriented design that complements our DDD and TDD approaches.

## Decision

We will apply SOLID principles throughout the codebase.

### Single Responsibility Principle (SRP)

Each class/module has one reason to change.

**Example:**
- `ShotRepository` handles shot persistence only
- `StablefordCalculator` handles scoring logic only
- `PinAuthenticator` handles authentication only

### Open/Closed Principle (OCP)

Open for extension, closed for modification.

**Example:**
- New scoring systems (e.g., stroke play) can be added without modifying existing Stableford code
- New club types can be added without changing shot recording logic

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types.

**Example:**
- Any `Repository` implementation (MongoDB, in-memory for tests) can be swapped without breaking the application
- Different `ScoringStrategy` implementations produce valid scores

### Interface Segregation Principle (ISP)

Clients should not depend on interfaces they don't use.

**Example:**
- `ReadOnlyRepository` for queries vs `Repository` for full CRUD
- Separate interfaces for `ShotRecorder` and `ShotAnalyzer`

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

**Example:**
- API endpoints depend on repository interfaces, not MongoDB directly
- Scoring services depend on `ShotProvider` interface, not specific data sources

### Practical application in Python:

```python
# Protocol for dependency inversion
class ShotRepository(Protocol):
    def save(self, shot: Shot) -> str: ...
    def find_by_club(self, club: str) -> list[Shot]: ...

# Concrete implementation
class MongoShotRepository:
    def save(self, shot: Shot) -> str: ...
    def find_by_club(self, club: str) -> list[Shot]: ...

# Service depends on abstraction
class ShotService:
    def __init__(self, repository: ShotRepository): ...
```

## Consequences

### Positive

- Highly testable code through dependency injection
- Easy to extend without modifying existing code
- Clear separation of concerns
- Supports DDD bounded contexts naturally

### Negative

- More abstractions and interfaces to maintain
- Can lead to over-engineering if applied dogmatically
- Requires discipline to identify proper boundaries

## References

- Robert C. Martin, "Clean Architecture"
- [SOLID Principles in Python](https://realpython.com/solid-principles-python/)
