Feature: Password Migration
    As an existing user with a weak password
    I want to be prompted to update my password
    So that my account meets the new security requirements

    Background:
        Given I am on the login screen

    Scenario: User with weak password is prompted to update
        Given a user exists with email "migrate@test.com" and weak password "1234"
        When I enter email "migrate@test.com"
        And I click the continue button
        And I enter password "1234"
        And I click the submit button
        Then I should see the password update form
        When I enter new password "SecurePass123"
        And I confirm new password "SecurePass123"
        And I click update password
        Then I should be logged in

    Scenario: Mismatched passwords show error
        Given a user exists with email "migrate2@test.com" and weak password "5678"
        When I enter email "migrate2@test.com"
        And I click the continue button
        And I enter password "5678"
        And I click the submit button
        Then I should see the password update form
        When I enter new password "SecurePass123"
        And I confirm new password "DifferentPass"
        And I click update password
        Then I should see password mismatch error
