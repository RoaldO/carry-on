Feature: Profile Display
  As a logged-in user
  I want to view my profile information
  So that I can see my account details and logout

  Background:
    Given a user exists with email "profile@example.com" and password "5678" and display name "Test Profile User"
    And I am logged in as "profile@example.com" with password "5678"

  Scenario: Profile tab shows user display name
    When I click the Profile tab
    Then I should see my display name "Test Profile User"

  Scenario: Profile tab shows user email
    When I click the Profile tab
    Then I should see my email "profile@example.com"

  Scenario: Logout button is visible on Profile tab
    When I click the Profile tab
    Then I should see the logout button

  Scenario: Clicking logout returns to login screen
    When I click the Profile tab
    And I click the logout button
    Then I should see the login screen
    And the tab bar should not be visible

  Scenario: Logout clears stored credentials
    When I click the Profile tab
    And I click the logout button
    And I reload the page
    Then I should see the login screen
