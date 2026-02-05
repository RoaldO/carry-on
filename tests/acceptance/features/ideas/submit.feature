Feature: Submit ideas
  As a logged-in user
  I want to submit feature ideas
  So I can provide feedback on the app

  Scenario: Submit an idea successfully
    Given an authenticated user
    And the user is on the Ideas tab
    When the user submits an idea "Add dark mode support"
    Then the idea submission is confirmed

  Scenario: Cannot submit empty idea
    Given an authenticated user
    And the user is on the Ideas tab
    When the user tries to submit an empty idea
    Then the form is not submitted

  Scenario: Character counter shows remaining characters
    Given an authenticated user
    And the user is on the Ideas tab
    When the user types an idea with 50 characters
    Then the character counter shows 950 remaining
