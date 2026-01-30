Feature: Record strokes
  As a logged-in user
  I want to record my strokes on the driving range
  So I can review my performance

  Scenario: Record a stroke
    Given an authenticated user
    When the user records a stroke
    Then the stroke is confirmed
