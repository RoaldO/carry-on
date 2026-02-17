Feature: Edit In-Progress Round
  As a logged-in user
  I want to click on an in-progress round to edit it
  So that I can continue recording strokes where I left off

  Background:
    Given a user with a 9-hole course "Pitch & Putt"
    And I am logged in and on the Rounds tab

  Scenario: In-progress rounds are clickable
    Given I have an in-progress round with 3 holes completed
    And I have a finished round
    When I view the recent rounds section
    Then the in-progress round should be clickable
    And finished rounds should not be clickable

  Scenario: Click in-progress round to edit it
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    Then I should see the hole navigator
    And the current hole should be 4
    And holes 1-3 should show the recorded strokes
    And I should see the par for the current hole

  Scenario: Auto-save current round before switching
    Given I start a new round for "Pitch & Putt"
    And I enter strokes "4" for hole 1
    And I have another in-progress round
    When I click on the other in-progress round
    Then the first round should be saved
    And the second round should be loaded
    And I should see the second round's data

  Scenario: Visual feedback for active round
    Given I have an in-progress round
    When I click on the in-progress round
    Then that round should be highlighted as active

  Scenario: Click in-progress round when not editing any round
    Given I have an in-progress round with 3 holes completed
    And I am not currently editing any round
    When I click on the in-progress round
    Then I should see the hole navigator without errors
    And the current hole should be 4

  Scenario: Continue adding holes to in-progress round
    Given I have an in-progress round with 3 holes completed
    When I click on the in-progress round
    And I enter strokes "6" for the current hole
    And I navigate away from the Rounds tab
    Then the round should still be in progress
    And the round should have 4 holes recorded
