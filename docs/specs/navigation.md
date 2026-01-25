# Feature: Tab Navigation

## Overview

Implement a tab-based navigation system to allow users to move between different sections of the app. This replaces the current single-page layout with a multi-tab interface.

## User Stories

- As a user, I want to navigate between different sections of the app using tabs, so that I can easily access all features
- As a user, I want to see which tab is currently active, so that I know where I am in the app
- As a user, I want to access my profile from the navigation, so that I can manage my account settings

## Requirements

### Functional Requirements

- FR-1: Tab bar is displayed at the bottom of the screen (mobile-first design)
- FR-2: Tab bar contains navigation to: Strokes, Ideas, Profile
- FR-3: Active tab is visually highlighted
- FR-4: Tapping a tab navigates to that section
- FR-5: Tab bar is persistent across all authenticated pages
- FR-6: Tab bar is not shown on login/activation screens

### Non-Functional Requirements

- NFR-1: Tab navigation should feel instant (no page reload)
- NFR-2: Navigation should work without JavaScript for basic functionality (progressive enhancement)
- NFR-3: Tab bar should be accessible (proper ARIA labels, keyboard navigation)

## UI/UX

### Tab Bar Design

```
┌─────────────────────────────────────┐
│                                     │
│           Page Content              │
│                                     │
├───────────┬───────────┬─────────────┤
│  Strokes  │   Ideas   │   Profile   │
│    ⛳     │    💡     │     👤      │
└───────────┴───────────┴─────────────┘
```

### Tabs

| Tab | Icon | Description |
|-----|------|-------------|
| Strokes | ⛳ (or golf icon) | Record and view golf strokes (current main page) |
| Ideas | 💡 (or lightbulb) | Submit and view ideas (current /ideas page) |
| Profile | 👤 (or person icon) | User profile and account settings |

### Tab States

- **Default**: Muted color, standard weight
- **Active**: Primary color (green), bold weight, filled icon
- **Pressed**: Slight scale down or color change for feedback

### Profile Page

The Profile tab displays:
- User's display name
- User's email address
- Logout button

Future additions (out of scope for this spec):
- Change password
- Account preferences

## Technical Approach

### Option A: Client-Side Routing (Recommended)

Use JavaScript to swap content without page reloads:
- Store all tab content in the same HTML
- Show/hide sections based on active tab
- Update URL hash for bookmarkability (`#strokes`, `#ideas`, `#profile`)

### Option B: Server-Side Pages

Separate HTML pages with shared tab bar component:
- `/` - Strokes page
- `/ideas` - Ideas page
- `/profile` - Profile page

### Recommendation

Option A (client-side) provides better UX with instant navigation. The app is already JavaScript-dependent for authentication, so this aligns with existing patterns.

## API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/me` | Get current user info for profile | Not implemented |

### GET /api/me

Returns the authenticated user's profile information.

**Request Headers**
```
X-Email: user@example.com
X-Pin: <pin>
```

**Response (200 OK)**
```json
{
  "email": "user@example.com",
  "display_name": "John Doe"
}
```

**Error Responses**
- `401 Unauthorized`: Not authenticated

## Acceptance Criteria

- [ ] Tab bar displays at bottom of screen on all authenticated pages
- [ ] Three tabs available: Strokes, Ideas, Profile
- [ ] Active tab is visually distinct
- [ ] Tapping tab navigates to corresponding section
- [ ] Profile page shows user's display name and email
- [ ] Profile page has logout button
- [ ] Logout clears credentials and returns to login screen
- [ ] Tab bar not shown on login/activation screens
- [ ] Navigation works on mobile and desktop

## Out of Scope

- Password/PIN change functionality (separate feature)
- User preferences/settings beyond basic profile
- Admin functionality
- Notification badges on tabs
