Feature: Add a Golf Course
  As a logged-in user
  I want to add a golf course with hole details
  So that I can track my rounds on that course

  Background:
    Given a user exists with email "courses@example.com" and password "Password5678!" and display name "Course User"
    And I am logged in as "courses@example.com" with password "Password5678!"
    And I navigate to the courses page

  Scenario: Add a 9-hole course
    When I click the add course button
    And I enter course name "Pitch & Putt"
    And I select 9 holes
    And I fill in the hole details for 9 holes
    And I submit the course form
    Then I should see "Pitch & Putt" in the course list

  Scenario: Course form validates empty name
    When I click the add course button
    And I submit the course form
    Then I should see a course form error

  Scenario: Courses page shows added courses after reload
    When I click the add course button
    And I enter course name "Reload Course"
    And I select 9 holes
    And I fill in the hole details for 9 holes
    And I submit the course form
    And I reload the courses page
    Then I should see "Reload Course" in the course list
