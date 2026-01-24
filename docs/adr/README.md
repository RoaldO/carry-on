# Architecture Decision Records

This directory contains the Architecture Decision Records (ADRs) for the CarryOn project.

All contributors MUST adhere to these decisions.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-domain-driven-development.md) | Domain-Driven Development | Accepted |
| [0002](0002-test-driven-development.md) | Test-Driven Development | Accepted |
| [0003](0003-solid-principles.md) | SOLID Principles | Accepted |
| [0004](0004-pytest.md) | pytest as Testing Framework | Accepted |
| [0005](0005-uv-package-manager.md) | uv for Dependency Management | Accepted |
| [0006](0006-owasp-security.md) | OWASP Security Best Practices | Accepted |
| [0007](0007-dependency-versioning.md) | Dependency Versioning Strategy | Accepted |
| [0008](0008-feature-specifications.md) | Feature Specifications | Accepted |

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences.

## Creating a new ADR

1. Copy the template below
2. Name the file `NNNN-short-title.md` (next sequential number)
3. Fill in the sections
4. Add to the index above
5. Submit for review

### Template

```markdown
# ADR NNNN: Title

## Status

Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](XXXX-title.md)

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?
```
