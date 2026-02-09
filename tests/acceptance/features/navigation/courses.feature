Feature: Course Management Navigation
  As a logged-in user
  I want to navigate to the course management page
  So that I can maintain my golf courses

  Background:
    Given a user exists with email "courses@example.com" and password "Password5678!" and display name "Course User"
    And I am logged in as "courses@example.com" with password "Password5678!"

  Scenario: Profile page shows My Courses link
    When I click the Profile tab
    Then I should see the "My Courses" link

  Scenario: Clicking My Courses navigates to courses page
    When I click the Profile tab
    And I click the "My Courses" link
    Then I should see the courses page
    And the Profile tab should be active

  Scenario: Courses page has back navigation to profile
    When I click the Profile tab
    And I click the "My Courses" link
    And I click the back link
    Then I should be on the Profile tab
