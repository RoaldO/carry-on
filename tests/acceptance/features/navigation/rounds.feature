Feature: Rounds Tab Navigation
  As a logged-in user
  I want to navigate to the Rounds tab
  So that I can register my golf rounds

  Background:
    Given a user exists with email "nav@example.com" and password "Password1234!"
    And I am logged in as "nav@example.com" with password "Password1234!"

  Scenario: Rounds tab is visible after login
    Then I should see the Rounds tab

  Scenario: Switch from Strokes to Rounds tab
    Given I am on the Strokes tab
    When I click the Rounds tab
    Then I should be on the Rounds tab
    And the Rounds tab should be active

  Scenario: Switch from Rounds to Ideas tab
    Given I am on the Rounds tab
    When I click the Ideas tab
    Then I should be on the Ideas tab
    And the Ideas tab should be active

  Scenario: URL hash updates to #rounds when clicking Rounds tab
    Given I am on the Strokes tab
    When I click the Rounds tab
    Then the URL should contain "#rounds"

  Scenario: Direct navigation via /#rounds URL hash
    When I navigate to "/#rounds"
    Then I should be on the Rounds tab
    And the Rounds tab should be active
