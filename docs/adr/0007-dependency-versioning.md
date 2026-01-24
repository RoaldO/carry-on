# ADR 0007: Dependency Versioning Strategy

## Status

Accepted

## Context

Dependencies evolve over time with bug fixes, security patches, and new features. We need a clear strategy for keeping dependencies up to date while maintaining stability. This is particularly important for security (see ADR-0006).

## Decision

We will follow an aggressive but controlled update strategy for dependencies that use semantic versioning (SemVer).

### Semantic Versioning recap

```
MAJOR.MINOR.PATCH (e.g., 2.5.3)
  │     │     └── Bug fixes, security patches (backward compatible)
  │     └──────── New features (backward compatible)
  └────────────── Breaking changes
```

### Our versioning requirements

#### PATCH updates (x.y.Z) - SHOULD use latest

- **Requirement**: SHOULD always be on the latest patch version
- **Rationale**: Patch releases contain bug fixes and security patches
- **Action**: Update immediately when available
- **Risk**: Minimal - patches are backward compatible

```toml
# Example: if 0.115.3 is latest patch for 0.115.x
"fastapi>=0.115.0"  # Will resolve to 0.115.3
```

#### MINOR updates (x.Y.z) - SHOULD upgrade ASAP

- **Requirement**: SHOULD upgrade to latest minor version as soon as possible
- **Rationale**: Minor releases contain new features and improvements, often including performance and security enhancements
- **Action**: Upgrade within days/weeks of release after verifying tests pass
- **Risk**: Low - minor versions are backward compatible

#### MAJOR updates (X.y.z) - Evaluate and plan

- **Requirement**: MAY upgrade after evaluation
- **Rationale**: Major versions may contain breaking changes
- **Action**: Review changelog, plan migration, update when beneficial
- **Risk**: Higher - may require code changes

### Implementation

#### In pyproject.toml

Use minimum version constraints allowing minor/patch updates:

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",    # Allow 0.115.x and 0.116.x, etc.
    "pymongo>=4.10.0",     # Allow 4.10.x and 4.11.x, etc.
    "pydantic>=2.0.0",     # Allow 2.x.x
]
```

#### Regular update process

```bash
# Check for outdated packages
uv pip list --outdated

# Update all dependencies to latest compatible versions
uv lock --upgrade

# Run tests to verify
uv run pytest

# If tests pass, commit the updated lock file
git add uv.lock
git commit -m "chore: update dependencies"
```

#### Scheduled updates

- **Weekly**: Check for and apply patch updates
- **Monthly**: Evaluate and apply minor updates
- **Quarterly**: Review major version updates

### Exceptions

For packages that don't follow SemVer strictly:
- Pin to known working version
- Document the reason
- Review more carefully before updating

## Consequences

### Positive

- Always have latest security fixes
- Benefit from bug fixes promptly
- Don't fall too far behind on features
- Easier incremental updates vs. big-bang upgrades

### Negative

- More frequent update cycles
- Occasional breaking changes despite SemVer promises
- Requires good test coverage to catch regressions

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [RFC 2119 - MUST/SHOULD/MAY](https://www.rfc-editor.org/rfc/rfc2119)
- [uv dependency management](https://docs.astral.sh/uv/)
