Feature: Session Persistence
  As a logged-in user
  I want my session to persist
  So that I don't have to log in repeatedly

  Background:
    Given a user exists with email "session@example.com" and password "5678"

  Scenario: Session persists across page reload
    Given I am on the login screen
    When I log in with email "session@example.com" and password "5678"
    Then I should be logged in
    When I reload the page
    Then I should still be logged in
    And the tab bar should be visible

  Scenario: Clearing localStorage logs out the user
    Given I am on the login screen
    When I log in with email "session@example.com" and password "5678"
    Then I should be logged in
    When I clear local storage
    And I reload the page
    Then I should see the login screen

  Scenario: Session allows accessing protected API endpoints
    Given I am on the login screen
    When I log in with email "session@example.com" and password "5678"
    Then I should be logged in
    And I should be able to view my strokes

  Scenario: Invalid stored credentials redirect to login
    Given I am on the login screen
    When I set invalid credentials in local storage
    And I reload the page
    Then I should see the login screen

  Scenario: Session persists when switching between tabs
    Given I am on the login screen
    When I log in with email "session@example.com" and password "5678"
    Then I should be logged in
    When I click the Ideas tab
    Then I should be on the Ideas tab
    When I click the Strokes tab
    Then I should be on the Strokes tab
    And I should still be logged in
