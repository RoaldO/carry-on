Feature: Register a Golf Round
  As a logged-in user
  I want to register a round by entering strokes for each hole
  So that I can track my golf performance

  Background:
    Given a user with a 9-hole course "Pitch & Putt"
    And I am logged in and on the Rounds tab

  Scenario: Round form shows date defaulting to today
    Then I should see the round date input with today's date

  Scenario: Course selector filters user courses
    When I type "Pitch" in the course search
    Then I should see "Pitch & Putt" in the course suggestions

  Scenario: Selecting a course shows hole navigator at hole 1
    When I type "Pitch" in the course search
    And I select "Pitch & Putt" from the suggestions
    Then I should see the hole navigator
    And the current hole should be 1
    And I should see the par for hole 1

  Scenario: Navigate between holes with arrows
    When I type "Pitch" in the course search
    And I select "Pitch & Putt" from the suggestions
    And I enter strokes "4" for the current hole
    And I click the next hole button
    Then the current hole should be 2
    When I click the previous hole button
    Then the current hole should be 1

  Scenario: Submit a complete 9-hole round
    When I type "Pitch" in the course search
    And I select "Pitch & Putt" from the suggestions
    And I fill all 9 holes with 4 strokes each
    And I click the submit round button
    Then I should see a round success message

  Scenario: View recent rounds history
    Given the user has completed rounds
    When I view the recent rounds section
    Then I should see recent rounds displayed
    And each round should show course name, date, and total strokes
