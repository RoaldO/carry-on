# Feature: Shot Tracking

## Overview

Record golf shot distances and failures per club per date. This is the core feature of CarryOn, allowing golfers to track their shot performance over time to understand their average distances with each club.

## User Stories

- As a golfer, I want to record the distance I hit with a specific club, so that I can track my performance over time
- As a golfer, I want to mark a shot as failed (topped, shanked, etc.), so that I can track my consistency
- As a golfer, I want to see my recent shots, so that I can verify my entries
- As a golfer, I want to quickly enter multiple shots in succession, so that I can efficiently log a practice session

## Requirements

### Functional Requirements

- FR-1: User can select a date for the shot (defaults to today)
- FR-2: User can select a club from a predefined list
- FR-3: User can enter a distance in meters (0-400)
- FR-4: User can mark a shot as "failed" instead of entering a distance
- FR-5: When a shot is marked as failed, distance is not required
- FR-6: After submitting, the form retains date and club selection for quick multi-entry
- FR-7: User can view the 5 most recent shots
- FR-8: All data is persisted to the database

### Non-Functional Requirements

- NFR-1: All API endpoints require PIN authentication (see ADR-0006)
- NFR-2: Form must be mobile-friendly for use on the golf course
- NFR-3: PIN is entered once per device and stored in localStorage

## Domain Model

### Entities

**Shot**
- `id`: Unique identifier (MongoDB ObjectId)
- `club`: Club used (string, e.g., "i7", "d", "pw")
- `distance`: Distance in meters (integer, nullable)
- `fail`: Whether the shot was a failure (boolean)
- `date`: Date the shot was taken (ISO date string)
- `created_at`: Timestamp when the record was created (ISO datetime string)

### Value Objects

**ClubType** (predefined list)
- Driver: `d`
- Woods: `3w`, `5w`
- Hybrids: `h4`, `h5`
- Irons: `i5`, `i6`, `i7`, `i8`, `i9`
- Wedges: `pw`, `gw`, `sw`, `lw`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the shot tracking form (HTML) |
| POST | `/api/verify-pin` | Verify PIN is correct |
| GET | `/api/shots` | List recent shots (requires PIN) |
| POST | `/api/shots` | Record a new shot (requires PIN) |

### POST /api/shots

**Request Headers**
```
Content-Type: application/json
X-Pin: <pin>
```

**Request Body**
```json
{
  "club": "i7",
  "distance": 150,
  "fail": false,
  "date": "2026-01-24"
}
```

**Response (200 OK)**
```json
{
  "id": "abc123",
  "message": "Shot recorded successfully",
  "shot": {
    "club": "i7",
    "distance": 150,
    "fail": false,
    "date": "2026-01-24"
  }
}
```

**Error Responses**
- `401 Unauthorized`: Invalid or missing PIN
- `400 Bad Request`: Distance required when fail is false

### GET /api/shots

**Request Headers**
```
X-Pin: <pin>
```

**Query Parameters**
- `limit`: Number of shots to return (default: 20)

**Response (200 OK)**
```json
{
  "shots": [
    {
      "id": "abc123",
      "club": "i7",
      "distance": 150,
      "fail": false,
      "date": "2026-01-24",
      "created_at": "2026-01-24T15:30:00Z"
    }
  ],
  "count": 1
}
```

## UI/UX

### PIN Entry Screen
- Full-screen overlay on first visit
- PIN input field (numeric keyboard on mobile)
- "Unlock" button
- Error message for invalid PIN

### Shot Entry Form
- **Date field**: Date picker, defaults to today
- **Club dropdown**: Select from predefined club list
- **Distance field**: Numeric input (disabled when fail is checked)
- **Fail checkbox**: Toggle for failed shots
- **Submit button**: "Record Shot"
- **Success message**: Shows recorded shot details for 3 seconds

### Recent Shots List
- Shows last 5 shots below the form
- Each shot displays: club (uppercase), distance or "FAIL", date
- Refreshes after each new submission

## Acceptance Criteria

- [x] PIN screen appears on first visit
- [x] Valid PIN grants access to the form
- [x] Invalid PIN shows error message
- [x] Date defaults to today
- [x] All clubs are available in dropdown
- [x] Distance field accepts numbers 0-400
- [x] Checking "fail" disables distance field
- [x] Submit with distance records shot with distance
- [x] Submit with fail records shot without distance
- [x] Submit without distance or fail shows error
- [x] Form retains date and club after submission
- [x] Recent shots list shows last 5 entries
- [x] Recent shots refresh after submission
- [x] Form is usable on mobile devices

## Out of Scope

- Shot statistics/averages (future feature)
- Shot location/GPS (future feature)
- Shot notes/comments
- Editing or deleting shots
- Filtering shots by date or club
