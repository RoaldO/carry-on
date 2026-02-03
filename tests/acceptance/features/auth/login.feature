Feature: User Login
  As a registered user
  I want to log in with my email and password
  So that I can access my golf stroke data

  Background:
    Given I am on the login screen

  Scenario: User logs in with valid credentials
    Given a user exists with email "active@example.com" and password "1234"
    When I enter email "active@example.com"
    And I click the continue button
    Then I should see the password login form
    And I should see "Welcome, Active User"
    When I enter password "1234"
    And I click the submit button
    Then I should be logged in
    And the tab bar should be visible

  Scenario: User enters incorrect password
    Given a user exists with email "active@example.com" and password "1234"
    When I enter email "active@example.com"
    And I click the continue button
    Then I should see the password login form
    When I enter password "9999"
    And I click the submit button
    Then I should see password error "Invalid email or password"

  Scenario: Already activated user sees login form not activation form
    Given a user exists with email "active@example.com" and password "1234"
    When I enter email "active@example.com"
    And I click the continue button
    Then I should see the password login form
    And the submit button should say "Login"
    And the confirm password field should not be visible

  Scenario: Session persists across page reload
    Given a user exists with email "active@example.com" and password "1234"
    When I enter email "active@example.com"
    And I click the continue button
    And I enter password "1234"
    And I click the submit button
    Then I should be logged in
    When I reload the page
    Then I should still be logged in
