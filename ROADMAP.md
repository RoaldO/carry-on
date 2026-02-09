# CarryOn Roadmap

## Planned Features
### 0r. Infer GitHub Actions from Project Configuration
Generate CI workflow from noxfile.py to avoid duplication and drift.
- [x] Evaluate approach (nox session to generate workflow, or template-based)
- [x] Create script/session to generate `.github/workflows/ci.yml`
- [x] Ensure generated workflow matches current CI behavior
- [x] Document regeneration process

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
- Measure stroke distances (club + distance per stroke)

### 5. GPS & Club Advice
- Mark hole locations by GPS when on the course (tee, green/pin)
- Store GPS coordinates per hole for later reference
- Get current location during round
- Calculate distance to hole
- Recommend clubs based on historical stroke data (average distance per club)
