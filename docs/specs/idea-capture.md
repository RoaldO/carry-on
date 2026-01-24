# Feature: In-App Idea Capture

## Overview

Allow users to submit feature ideas and feedback directly from within the app. Ideas are stored in the database for later review by the developer.

## User Stories

- As a user, I want to submit a feature idea while using the app, so that I don't forget it
- As a user, I want to provide feedback about the app, so that it can be improved
- As a developer, I want to see submitted ideas, so that I can prioritize features

## Requirements

### Functional Requirements

- FR-1: User can access an "Ideas" section from the main interface
- FR-2: User can enter a text description of their idea (required, max 1000 chars)
- FR-3: User can submit the idea with a single tap
- FR-4: Submitted ideas are stored in the database with a timestamp
- FR-5: User sees a confirmation message after successful submission
- FR-6: Form clears after successful submission for quick multi-entry

### Non-Functional Requirements

- NFR-1: All API endpoints require PIN authentication
- NFR-2: Ideas are stored in a separate MongoDB collection (`ideas`)

## Domain Model

### Entities

**Idea**
- `id`: Unique identifier (MongoDB ObjectId)
- `description`: Text description of the idea (string, max 1000 chars)
- `created_at`: Timestamp when the idea was submitted (ISO datetime string)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ideas` | Submit a new idea (requires PIN) |
| GET | `/api/ideas` | List all ideas (requires PIN) |

### POST /api/ideas

**Request Headers**
```
Content-Type: application/json
X-Pin: <pin>
```

**Request Body**
```json
{
  "description": "Add ability to track putts separately"
}
```

**Response (200 OK)**
```json
{
  "id": "abc123",
  "message": "Idea submitted successfully",
  "idea": {
    "description": "Add ability to track putts separately",
    "created_at": "2026-01-24T16:00:00Z"
  }
}
```

**Error Responses**
- `401 Unauthorized`: Invalid or missing PIN
- `422 Unprocessable Entity`: Description missing, empty, or exceeds 1000 characters

### GET /api/ideas

**Request Headers**
```
X-Pin: <pin>
```

**Query Parameters**
- `limit`: Number of ideas to return (default: 50)

**Response (200 OK)**
```json
{
  "ideas": [
    {
      "id": "abc123",
      "description": "Add ability to track putts separately",
      "created_at": "2026-01-24T16:00:00Z"
    }
  ],
  "count": 1
}
```

## UI/UX

### Access Point
- Add "Ideas" link/button below the recent shots section

### Idea Submission Form
- **Description field**: Textarea for idea description (required)
- **Character counter**: Show remaining characters (max 1000)
- **Submit button**: "Submit Idea"
- **Success message**: "Idea submitted!" shown for 3 seconds

## Acceptance Criteria

- [ ] "Ideas" section accessible from main interface
- [ ] Can enter idea description up to 1000 characters
- [ ] Character counter shows remaining characters
- [ ] Submit without description shows error
- [ ] Submit with description > 1000 chars shows error
- [ ] Successful submit shows confirmation message
- [ ] Form clears after successful submission
- [ ] Ideas stored in database with timestamp
- [ ] GET /api/ideas returns submitted ideas
- [ ] All endpoints require PIN authentication

## Out of Scope

- Editing or deleting ideas
- Categorizing ideas
- Voting on ideas
- Admin interface for reviewing ideas
