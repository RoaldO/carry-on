# ADR 0010: Usability - Navigation and Interaction Limits

## Status

Accepted

## Context

CarryOn is a mobile-first web application designed for use on the golf course. Users need to quickly access features while playing, often with limited attention and potentially difficult conditions (bright sunlight, one-handed operation, time pressure between shots).

Complex navigation hierarchies and deeply nested menus create friction and frustration, especially in a sports context where quick access is essential.

## Decision

We will enforce two usability rules:

### Two-Click Navigation

1. **Any feature or action must be reachable within two clicks** from the main screen after authentication.

2. **The tab bar serves as the primary navigation** mechanism, providing one-click access to major sections (Strokes, Ideas, Profile).

3. **Within each section**, all actions must be immediately available or require at most one additional click.

### Three-Tap Task Completion

Once on the correct page, **any task must be completable in three taps or fewer**. This includes all required form inputs and the final submission.

1. **Required interactions count toward the limit** - selecting a dropdown, entering text, checking a box, and tapping submit each count as one tap.

2. **Optional fields don't count** - fields with sensible defaults that users can skip don't add to the count.

3. **Destructive actions may add one confirmation** - delete operations may include a confirmation dialog, but this is the only exception.

### Examples

**Navigation (two-click rule):**

| Action | Clicks | Path |
|--------|--------|------|
| Record a stroke | 0 | Already on Strokes tab |
| Submit an idea | 1 | Click Ideas tab |
| View recent strokes | 0 | Already visible on Strokes tab |
| Log out | 2 | Profile tab → Logout button |
| Change settings | 2 | Profile tab → Settings option |

**Task completion (three-tap rule):**

| Task | Taps | Interactions |
|------|------|--------------|
| Record a stroke | 3 | Select club → Enter distance → Submit |
| Record failed stroke | 2 | Select club → Check "failed" (auto-submits or tap submit) |
| Submit an idea | 2 | Type idea → Submit |
| Delete a stroke | 2 | Tap delete → Confirm |

### Implementation Guidelines

- Prefer flat navigation over nested hierarchies
- Use modal dialogs or inline expansion rather than new pages for secondary actions
- Keep the tab bar visible on all authenticated screens
- Avoid "wizard" flows with multiple steps where possible
- If a flow requires more than two steps, consider it a single logical action (e.g., login flow)

## Consequences

### Positive

- Fast, frictionless access to all features
- Quick task completion even under time pressure
- Better usability on mobile devices and in outdoor conditions
- Reduced cognitive load for users
- Forces simplicity in feature design
- Forms stay focused and minimal

### Negative

- Limits the depth of feature hierarchies
- Complex tasks must be split or simplified
- May require creative UI solutions (smart defaults, auto-submit, combined fields)
- Tab bar takes up screen real estate
- New features must be carefully designed to maintain both rules
