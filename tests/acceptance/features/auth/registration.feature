Feature: User Registration
  As a new user
  I want to activate my account with a PIN
  So that I can use the CarryOn app

  Background:
    Given I am on the login screen

  Scenario: User activates account with valid email and PIN
    Given a user exists with email "inactive@example.com" who needs activation
    When I enter email "inactive@example.com"
    And I click the continue button
    Then I should see the PIN activation form
    And I should see "Welcome, Inactive User"
    When I enter PIN "SecureP1"
    And I enter confirm PIN "SecureP1"
    And I click the submit button
    Then I should be logged in
    And the tab bar should be visible

  Scenario: User enters mismatched PINs during activation
    Given a user exists with email "inactive@example.com" who needs activation
    When I enter email "inactive@example.com"
    And I click the continue button
    Then I should see the PIN activation form
    When I enter PIN "SecureP1"
    And I enter confirm PIN "SecureP2"
    And I click the submit button
    Then I should see PIN error "Passwords do not match"

  Scenario: User enters unregistered email
    When I enter email "unknown@example.com"
    And I click the continue button
    Then I should see email error "Email not registered. Contact administrator."

  Scenario: User can go back from PIN step to email step
    Given a user exists with email "inactive@example.com" who needs activation
    When I enter email "inactive@example.com"
    And I click the continue button
    Then I should see the PIN activation form
    When I click the back button
    Then I should see the email form
