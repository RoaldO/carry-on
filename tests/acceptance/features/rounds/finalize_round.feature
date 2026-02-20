Feature: Finalize a Golf Round
  As a logged-in user editing a round
  I want separate "Save Progress" and "Finish Round" buttons
  So that I have explicit control over saving vs finishing

  Background:
    Given a user with a 9-hole course "Pitch & Putt"
    And I am logged in and on the Rounds tab

  Scenario: Two buttons visible when editing an in-progress round
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    Then I should see the "Save Progress" button
    And I should see the "Finish Round" button

  Scenario: Two buttons visible when starting a new round
    When I type "Pitch" in the course search
    And I select "Pitch & Putt" from the suggestions
    Then I should see the "Save Progress" button
    And I should see the "Finish Round" button

  Scenario: Save Progress saves and resets form
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    And I enter strokes "3" for the current hole
    And I click the "Save Progress" button
    Then I should see a progress saved message
    And the round should still be in progress

  Scenario: Finish Round finishes a complete 9-hole round
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    And I fill the remaining holes with 4 strokes each
    And I click the "Finish Round" button
    Then I should see a round finished message

  Scenario: Finish Round disabled when fewer than 9 holes filled
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    Then the "Finish Round" button should be disabled

  Scenario: Finish Round enabled when all 9 holes filled
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    And I fill the remaining holes with 4 strokes each
    Then the "Finish Round" button should be enabled
