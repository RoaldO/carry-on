# CarryOn Roadmap

## Current Features
- Record golf shots (club, distance, fail)
- View recent shots
- PIN authentication

## Planned Features

### 0. Test, Build & Deploy Tooling
- [x] Set up pytest for backend testing
- [x] Add API endpoint tests
- [x] CI/CD pipeline (GitHub Actions)
- [x] Automated deployment to Vercel on push

### 0b. In-App Idea Capture
- Submit new feature ideas/feedback from within the app
- Store ideas in database for later review

### 1. Golf Course Management
Store golf course information including:
- Course name
- Number of holes (9/18)
- Par per hole
- Stroke index per hole (for handicap allocation)

### 2. Player Handicap
- Store player handicap index
- Support for course handicap calculation based on course rating/slope

### 3. Stableford Score Calculation
- Calculate Stableford points per hole based on:
  - Net strokes (gross - handicap strokes)
  - Par for the hole
- Show running Stableford total during round
- Store completed rounds with final scores

### 4. Round Tracking
Use the app during a round to:
- Select a course
- Track strokes per hole
- Tally total hits in real-time
- Mark penalties, putts, etc.
- Measure shot distances (club + distance per shot)

### 5. GPS & Club Advice
- Mark hole locations by GPS when on the course (tee, green/pin)
- Store GPS coordinates per hole for later reference
- Get current location during round
- Calculate distance to hole
- Recommend clubs based on historical shot data (average distance per club)
