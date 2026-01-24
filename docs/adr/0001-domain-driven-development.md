# ADR 0001: Domain-Driven Development

## Status

Accepted

## Context

CarryOn is a golf shot tracking application that will grow to include features like course management, round tracking, handicap calculation, and Stableford scoring. As the domain logic becomes more complex, we need a clear architectural approach to keep the codebase maintainable and aligned with the golf domain.

## Decision

We will use Domain-Driven Development (DDD) principles to structure the application.

### Key practices we will follow:

1. **Ubiquitous Language**: Use golf terminology consistently throughout the codebase (e.g., `Shot`, `Round`, `Course`, `Hole`, `Handicap`, `Stableford`).

2. **Domain Models**: Create rich domain models that encapsulate golf-related business logic rather than anemic data structures.

3. **Bounded Contexts**: Separate distinct areas of the application:
   - Shot Tracking (current feature)
   - Course Management
   - Round Management
   - Scoring (Stableford, handicap calculations)
   - Player Profile

4. **Aggregates**: Group related entities that should be treated as a unit (e.g., a `Round` aggregate containing `Hole` scores).

5. **Value Objects**: Use immutable value objects for concepts like `Distance`, `ClubType`, `StablefordPoints`.

6. **Repository Pattern**: Abstract data persistence behind repository interfaces.

## Consequences

### Positive

- Code structure mirrors the golf domain, making it intuitive for developers
- Business logic is centralized in domain models, not scattered across endpoints
- Easier to add new features within existing bounded contexts
- Better testability through domain model unit tests

### Negative

- Initial overhead in setting up proper domain structure
- May feel over-engineered for simple CRUD operations
- Team needs to understand DDD concepts

## References

- Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software"
- Vaughn Vernon, "Implementing Domain-Driven Design"
