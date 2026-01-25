# Feature: Stroke Tracking

## Overview

Record golf stroke distances and failures per club per date. This is the core feature of CarryOn, allowing golfers to track their stroke performance over time to understand their average distances with each club.

## User Stories

- As a golfer, I want to record the distance I hit with a specific club, so that I can track my performance over time
- As a golfer, I want to mark a stroke as failed (topped, shanked, etc.), so that I can track my consistency
- As a golfer, I want to see my recent strokes, so that I can verify my entries
- As a golfer, I want to quickly enter multiple strokes in succession, so that I can efficiently log a practice session

## Requirements

### Functional Requirements

- FR-1: User can select a date for the stroke (defaults to today)
- FR-2: User can select a club from a predefined list
- FR-3: User can enter a distance in meters (0-400)
- FR-4: User can mark a stroke as "failed" instead of entering a distance
- FR-5: When a stroke is marked as failed, distance is not required
- FR-6: After submitting, the form retains date and club selection for quick multi-entry
- FR-7: User can view the 5 most recent strokes
- FR-8: All data is persisted to the database

### Non-Functional Requirements

- NFR-1: All API endpoints require PIN authentication (see ADR-0006)
- NFR-2: Form must be mobile-friendly for use on the golf course
- NFR-3: PIN is entered once per device and stored in localStorage

## Domain Model

### Entities

**Stroke**
- `id`: Unique identifier (MongoDB ObjectId)
- `club`: Club used (string, e.g., "i7", "d", "pw")
- `distance`: Distance in meters (integer, nullable)
- `fail`: Whether the stroke was a failure (boolean)
- `date`: Date the stroke was taken (ISO date string)
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
| GET | `/` | Serve the stroke tracking form (HTML) |
| POST | `/api/verify-pin` | Verify PIN is correct |
| GET | `/api/strokes` | List recent strokes (requires PIN) |
| POST | `/api/strokes` | Record a new stroke (requires PIN) |

### POST /api/strokes

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
  "message": "Stroke recorded successfully",
  "stroke": {
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

### GET /api/strokes

**Request Headers**
```
X-Pin: <pin>
```

**Query Parameters**
- `limit`: Number of strokes to return (default: 20)

**Response (200 OK)**
```json
{
  "strokes": [
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

### Stroke Entry Form
- **Date field**: Date picker, defaults to today
- **Club dropdown**: Select from predefined club list
- **Distance field**: Numeric input (disabled when fail is checked)
- **Fail checkbox**: Toggle for failed strokes
- **Submit button**: "Record Stroke"
- **Success message**: Shows recorded stroke details for 3 seconds

### Recent Strokes List
- Shows last 5 strokes below the form
- Each stroke displays: club (uppercase), distance or "FAIL", date
- Refreshes after each new submission

## Acceptance Criteria

- [x] PIN screen appears on first visit
- [x] Valid PIN grants access to the form
- [x] Invalid PIN shows error message
- [x] Date defaults to today
- [x] All clubs are available in dropdown
- [x] Distance field accepts numbers 0-400
- [x] Checking "fail" disables distance field
- [x] Submit with distance records stroke with distance
- [x] Submit with fail records stroke without distance
- [x] Submit without distance or fail shows error
- [x] Form retains date and club after submission
- [x] Recent strokes list shows last 5 entries
- [x] Recent strokes refresh after submission
- [x] Form is usable on mobile devices

## Out of Scope

- Stroke statistics/averages (future feature)
- Stroke location/GPS (future feature)
- Stroke notes/comments
- Editing or deleting strokes
- Filtering strokes by date or club
