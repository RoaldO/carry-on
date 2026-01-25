# Feature: Multi-User Support

## Overview

Transition from single-user PIN authentication to a multi-user system where each user has their own account. Users are added by the administrator via the database and activate their accounts using their email address.

## User Stories

- As an administrator, I want to add users directly to the database, so that I control who has access
- As an invited user, I want to activate my account using my email address, so that I can start using the app
- As a user, I want my shots and ideas to be private to my account, so that my data is separate from other users

## Requirements

### Functional Requirements

- FR-1: Administrator adds users to a `users` collection via database interface (no self-registration)
- FR-2: User record contains at minimum: email address, display name, and activation status
- FR-3: User can activate their account by entering their email address
- FR-4: Upon first activation, user sets a PIN for future logins
- FR-5: Activated users log in using email + PIN
- FR-6: All shots are associated with a user ID
- FR-7: All ideas are associated with a user ID
- FR-8: Users can only view and create their own shots and ideas

### Non-Functional Requirements

- NFR-1: Email addresses must be unique in the system
- NFR-2: PINs are stored securely (hashed with Argon2id) - see [ADR-0009](../adr/0009-password-hashing.md)
- NFR-3: Existing shots/ideas are migrated to a default user account

## Domain Model

### Entities

**User**
- `id`: Unique identifier (MongoDB ObjectId)
- `email`: Email address (unique, lowercase)
- `display_name`: User's display name
- `pin_hash`: Hashed PIN (null until activated)
- `activated_at`: Timestamp of activation (null until activated)
- `created_at`: Timestamp when admin created the record

### Updated Entities

**Shot** (updated)
- `user_id`: Reference to User (required)
- ... existing fields

**Idea** (updated)
- `user_id`: Reference to User (required)
- ... existing fields

## API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/check-email` | Check if email exists and activation status | Done |
| POST | `/api/activate` | Activate account and set PIN | Done |
| POST | `/api/login` | Login with email + PIN | Done |
| GET | `/api/me` | Get current user info | Not implemented |

### POST /api/check-email

Check if an email exists in the system and its activation status.

**Request Body**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK) - Needs activation**
```json
{
  "status": "needs_activation",
  "display_name": "John Doe"
}
```

**Response (200 OK) - Already activated**
```json
{
  "status": "activated",
  "display_name": "John Doe"
}
```

**Error Responses**
- `404 Not Found`: Email not found in system

### POST /api/activate

**Request Body**
```json
{
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response (200 OK)**
```json
{
  "message": "Account activated successfully",
  "user": {
    "email": "user@example.com",
    "display_name": "John Doe"
  }
}
```

**Error Responses**
- `404 Not Found`: Email not found in system
- `400 Bad Request`: Account already activated
- `422 Unprocessable Entity`: Invalid PIN format

### POST /api/login

**Request Body**
```json
{
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response (200 OK)**
```json
{
  "message": "Login successful",
  "user": {
    "email": "user@example.com",
    "display_name": "John Doe"
  },
  "token": "<session_token>"
}
```

**Error Responses**
- `401 Unauthorized`: Invalid email or PIN
- `400 Bad Request`: Account not yet activated

### Authentication Header

All authenticated API requests use email and PIN headers:
```
X-Email: user@example.com
X-Pin: <pin>
```

The frontend stores these credentials in localStorage after successful login/activation and sends them with each request.

## UI/UX

### Login Screen (replaces PIN screen)

1. **Email input**: User enters their email address
2. **Check account status**:
   - If not found → "Email not registered. Contact administrator."
   - If not activated → Show PIN setup form
   - If activated → Show PIN input form

### Activation Flow

1. User enters email
2. System confirms email exists and is not activated
3. User sets their PIN (with confirmation)
4. Account is activated
5. User is logged in

### Login Flow

1. User enters email
2. User enters PIN
3. System validates credentials
4. User is logged in

## Database Setup (Admin)

To add a new user, insert directly into MongoDB:

```javascript
db.users.insertOne({
  email: "user@example.com",
  display_name: "John Doe",
  pin_hash: null,
  activated_at: null,
  created_at: new Date()
})
```

## Migration Plan

1. Create `users` collection
2. Create a default admin user
3. Add `user_id` field to existing shots (set to admin user)
4. Add `user_id` field to existing ideas (set to admin user)
5. Update all API endpoints to require user context
6. Update UI to use new login flow

## Acceptance Criteria

- [x] Admin can add users via database
- [x] New users can activate with email + set PIN
- [x] Activated users can log in with email + PIN
- [x] PINs are securely hashed with Argon2id
- [x] Legacy plain text PINs are auto-migrated on login
- [ ] Shots are associated with logged-in user
- [ ] Ideas are associated with logged-in user
- [ ] Users cannot see other users' data
- [ ] Existing data is migrated to default user
- [x] PIN screen replaced with email/PIN login

## Out of Scope

- User self-registration
- Password reset (admin resets by clearing pin_hash)
- Email verification
- Admin UI for user management
- User roles/permissions
