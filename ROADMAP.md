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
- [x] Submit new feature ideas/feedback from within the app
- [x] Store ideas in database for later review
- [x] Move "Submit an Idea" to a less intrusive location

### 0c. Refactor to DDD/SOLID (ADR Compliance)
Refactor codebase to follow ADR-0001 (DDD) and ADR-0003 (SOLID):
- [ ] Create domain layer (`domain/shot.py`) with Shot entity and value objects
- [ ] Create repository layer (`repositories/shot_repository.py`) with abstract interface
- [ ] Create service layer (`services/shot_service.py`) for business logic
- [ ] Refactor `api/index.py` to only handle routing, delegate to services
- [ ] Update tests to use dependency injection

### 0d. Dependency Version Audit (ADR-0007 Compliance)
- [ ] Check all dependencies are on latest patch version
- [ ] Upgrade to latest minor versions where available

### 0e. Code Coverage
- [x] Add pytest-cov for coverage reporting
- [x] Add coverage check to CI pipeline
- [x] Set minimum coverage threshold (70%)

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
