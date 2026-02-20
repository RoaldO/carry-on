# Feature: Round Finalization

## Overview

Provide explicit control over whether to save progress or finish a round. Replace the
single "Submit Round" button with two distinct actions: **Save Progress** and
**Finish Round**.

## User Stories

- As a golfer editing a round, I want to save my progress without finishing, so that I
  can continue the round later.
- As a golfer who has completed all holes, I want to explicitly finish the round, so
  that it is marked as completed.
- As a golfer, I want to see that "Finish Round" is disabled when holes are missing, so
  that I don't accidentally submit an incomplete round.

## Requirements

### Functional Requirements

- FR-1: Two buttons are shown when editing a round: "Save Progress" and "Finish Round"
- FR-2: "Save Progress" saves the current hole, shows a confirmation message, and resets
  the form so the user can start or edit another round
- FR-3: "Finish Round" saves the current hole, calls the finish endpoint, shows a
  success message, and resets the form
- FR-4: "Finish Round" is disabled when fewer than 9 (or 18) holes have strokes entered
- FR-5: "Finish Round" is enabled when all holes for the course have strokes entered
- FR-6: Both buttons are visible when starting a new round (after selecting a course)

### Non-Functional Requirements

- NFR-1: No backend changes required — uses existing `PATCH /api/rounds/{id}/status?action=finish`
- NFR-2: Buttons must be usable on mobile (adequate tap targets)

## Acceptance Criteria

- AC-1: When editing an in-progress round, two buttons ("Save Progress" and
  "Finish Round") are visible
- AC-2: When starting a new round (course selected), the same two buttons are visible
- AC-3: Clicking "Save Progress" saves progress and resets the form; the round stays
  in-progress
- AC-4: Clicking "Finish Round" on a complete 9-hole round finishes it successfully
- AC-5: "Finish Round" is disabled when fewer than 9 holes are filled
- AC-6: "Finish Round" becomes enabled when exactly 9 holes are filled
