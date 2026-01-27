# ADR 0011: Specification Acceptance Tests

## Status

Accepted

## Context

ADR-0008 establishes that all features must have specifications with acceptance criteria. ADR-0002 mandates test-driven development. However, there is no explicit requirement linking specifications to automated acceptance tests.

Manual verification of acceptance criteria is error-prone and doesn't scale. As the application grows, we need confidence that specifications remain accurate and features continue to work as documented.

## Decision

Every feature specification MUST have corresponding acceptance tests written in Gherkin format using pytest-bdd.

### Requirements

1. **Each specification file must have a matching feature file** in `tests/acceptance/features/` that covers its acceptance criteria.

2. **Feature files use Gherkin syntax** to describe behavior in plain language that matches the specification.

3. **Acceptance tests run against the real UI** using Playwright, validating end-to-end behavior.

### File Structure

```
docs/specs/
├── stroke-tracking.md          # Specification
├── multi-user.md
└── navigation.md

tests/acceptance/features/
├── strokes/
│   └── stroke-tracking.feature  # Acceptance tests for stroke-tracking.md
├── auth/
│   ├── registration.feature     # Acceptance tests for multi-user.md
│   └── login.feature
└── navigation/
    └── tab-navigation.feature   # Acceptance tests for navigation.md
```

### Workflow

1. **Write specification** with acceptance criteria (ADR-0008)
2. **Create feature file** translating acceptance criteria to Gherkin scenarios
3. **Write step definitions** and page objects
4. **Run tests** - they should fail (TDD red phase)
5. **Implement feature** until tests pass (TDD green phase)
6. **Refactor** as needed

### Example

Specification (`docs/specs/stroke-tracking.md`):
```markdown
## Acceptance Criteria
- [ ] User can record a stroke with club and distance
- [ ] User can mark a stroke as failed
- [ ] Recent strokes are displayed after recording
```

Feature file (`tests/acceptance/features/strokes/stroke-tracking.feature`):
```gherkin
Feature: Stroke Tracking
  As a golfer
  I want to record my strokes
  So that I can track my performance

  Scenario: Record a stroke with club and distance
    Given I am logged in
    And I am on the Strokes tab
    When I select club "i7"
    And I enter distance "150"
    And I click Record Stroke
    Then I should see a success message
    And the stroke should appear in recent strokes

  Scenario: Record a failed stroke
    Given I am logged in
    And I am on the Strokes tab
    When I select club "d"
    And I check "Failed stroke"
    And I click Record Stroke
    Then I should see a success message
    And the stroke should show as "FAIL"
```

### Traceability

- Feature file scenarios should map to specification acceptance criteria
- Use comments in feature files to reference specification requirements: `# Covers: AC-1, AC-2`

## Consequences

### Positive

- Specifications become executable documentation
- Acceptance criteria are automatically verified
- Regressions are caught immediately
- Living documentation that stays in sync with behavior
- Clear definition of "done" for features

### Negative

- Additional effort to write and maintain feature files
- Acceptance tests are slower than unit tests
- Requires Playwright browser installation in CI
- Step definitions need maintenance as UI changes

## References

- [ADR-0002: Test-Driven Development](0002-test-driven-development.md)
- [ADR-0008: Feature Specifications](0008-feature-specifications.md)
- [Specification by Example](https://en.wikipedia.org/wiki/Specification_by_example)
- [pytest-bdd documentation](https://pytest-bdd.readthedocs.io/)
