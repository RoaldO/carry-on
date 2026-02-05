Feature: Record strokes
  As a logged-in user
  I want to record my strokes on the driving range
  So I can review my performance

  Scenario: Record a successful stroke with distance
    Given an authenticated user
    When the user records a stroke with distance 150
    Then the stroke is confirmed with distance 150

  Scenario: Record a failed stroke
    Given an authenticated user
    When the user records a failed stroke
    Then the stroke is confirmed as failed

  Scenario: View recent strokes
    Given an authenticated user
    And the user has recorded strokes
    When the user views recent strokes
    Then the recent strokes are displayed

  Scenario: Validation requires distance or fail
    Given an authenticated user
    When the user submits a stroke without distance or fail
    Then an error message is shown
