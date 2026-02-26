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
- [x] Course name
- [x] Number of holes (9/18)
- [x] Par per hole
- [x] Stroke index per hole (for handicap allocation)
- [x] Course creation form and list UI
- [x] Course detail endpoint (GET /api/courses/{id} with hole data)

### 2. Player Handicap
- [x] Store player handicap index (snapshot on Round at creation)
- [x] Course handicap calculation using WHS formula (slope/course rating)
- [x] Fallback rounding when slope/course rating not available
- [x] Default to WHS maximum (54) when no player handicap set
- [x] Slope rating and course rating on Course and Round aggregates

### 3. Stableford Score Calculation
- [x] Handicap stroke distribution by stroke index (hardest holes first)
- [x] Per-hole Stableford points (auto-computed on record/update)
- [x] Per-hole handicap strokes stored for scoring transparency
- [x] Total Stableford score calculated on round finalization
- [x] Backfill per-hole points and handicap strokes on finish for legacy rounds
- [ ] Show running Stableford total during round (UI)

### 4. Round Tracking
Use the app during a round to:
- [x] Select a course (type-ahead course selector)
- [x] Track strokes per hole (hole navigator with prev/next)
- [x] Submit completed rounds (POST /api/rounds)
- [x] View recorded rounds (GET /api/rounds)
- [ ] Tally total hits in real-time
- [ ] Mark penalties, putts, etc.
- [ ] Measure stroke distances (club + distance per stroke)

### 5. GPS & Club Advice
- Mark hole locations by GPS when on the course (tee, green/pin)
- Store GPS coordinates per hole for later reference
- Get current location during round
- Calculate distance to hole
- Recommend clubs based on historical stroke data (average distance per club)
