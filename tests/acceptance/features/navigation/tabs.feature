Feature: Tab Navigation
  As a logged-in user
  I want to navigate between different sections using tabs
  So that I can easily access all features of the app

  Background:
    Given a user exists with email "nav@example.com" and PIN "1234"
    And I am logged in as "nav@example.com" with PIN "1234"

  Scenario: Tab bar is visible after login
    Then the tab bar should be visible
    And I should see the Strokes tab
    And I should see the Ideas tab
    And I should see the Profile tab

  Scenario: Switch from Strokes to Ideas tab
    Given I am on the Strokes tab
    When I click the Ideas tab
    Then I should be on the Ideas tab
    And the Ideas tab should be active

  Scenario: Switch from Ideas to Profile tab
    Given I am on the Ideas tab
    When I click the Profile tab
    Then I should be on the Profile tab
    And the Profile tab should be active

  Scenario: Switch from Profile to Strokes tab
    Given I am on the Profile tab
    When I click the Strokes tab
    Then I should be on the Strokes tab
    And the Strokes tab should be active

  Scenario: URL hash updates when switching tabs
    Given I am on the Strokes tab
    When I click the Ideas tab
    Then the URL should contain "#ideas"
    When I click the Profile tab
    Then the URL should contain "#profile"
    When I click the Strokes tab
    Then the URL should contain "#strokes"

  Scenario: Direct navigation via URL hash
    When I navigate to "/#ideas"
    Then I should be on the Ideas tab
    When I navigate to "/#profile"
    Then I should be on the Profile tab
    When I navigate to "/#strokes"
    Then I should be on the Strokes tab

  Scenario: Tab bar is hidden on login screen
    When I logout
    Then the tab bar should not be visible
