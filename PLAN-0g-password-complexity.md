# 0g. Password Complexity Support - Implementation Plan

## Summary

Migrate from 4-digit numeric PINs to full password support (min 8 chars, any characters) with a migration flow for existing users.

## Migration Flow

1. User logs in with old weak PIN (e.g., "1234")
2. API validates PIN is correct but returns `status: "password_update_required"`
3. UI shows password update screen with message about new requirements
4. User enters new compliant password (min 8 chars)
5. API updates password hash, user proceeds to app

## Implementation Steps (TDD)

### Phase 1: Backend - Password Complexity Validation

**Step 1.1** - Write failing tests for `is_password_compliant()`
- File: `tests/test_password_security.py`
- Tests: min 8 chars, no max limit, accepts any characters

**Step 1.2** - Implement `is_password_compliant()` in `api/pin_security.py`
- Simple length check: `len(password) >= 8`

**Step 1.3** - Update Pydantic models
- `ActivateRequest`: rename `pin` to `password`, min_length=8, remove max
- `LoginRequest`: rename `pin` to `password`, keep min_length=4 (for migration)

### Phase 2: Backend - Migration Login Flow

**Step 2.1** - Write failing tests for login migration response
- File: `tests/test_auth_api.py`
- Test: login with weak password returns `{"status": "password_update_required"}`
- Test: login with compliant password returns `{"status": "success"}`

**Step 2.2** - Modify `/api/login` endpoint
- After successful auth, check `is_password_compliant()`
- If not compliant, return `status: "password_update_required"`

**Step 2.3** - Write failing tests for `/api/update-password`
- Test: requires valid current password
- Test: validates new password complexity
- Test: updates hash on success

**Step 2.4** - Implement `/api/update-password` endpoint
```python
class UpdatePasswordRequest(BaseModel):
    email: str
    current_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=8)
```

### Phase 3: Backend - Rename PIN to Password

**Step 3.1** - Update header verification
- Support both `X-Pin` and `X-Password` headers (backwards compat)
- Prefer `X-Password` when both present

**Step 3.2** - Update function names
- `verify_pin()` -> `verify_password()`
- `hash_pin()` -> `hash_password()`
- Keep `pin_hash` field in DB for now (less invasive)

### Phase 4: Frontend Updates

**Step 4.1** - Update HTML
- Remove `inputmode="numeric" pattern="[0-9]*"` from password inputs
- Change labels: "PIN" -> "Password", "Create your PIN" -> "Create your Password"
- Add password update step (`<div id="stepUpdatePassword">`)

**Step 4.2** - Update JavaScript
- localStorage: `carryon_pin` -> `carryon_password`
- Headers: `X-Pin` -> `X-Password`
- Handle `password_update_required` response from login
- Add password update form handler

### Phase 5: Acceptance Tests

**Step 5.1** - Update existing tests
- Rename PIN references to password
- Update test data to use 8+ char passwords

**Step 5.2** - Add migration feature
- File: `tests/acceptance/features/auth/password_migration.feature`
- Scenario: weak password prompts update
- Scenario: mismatched passwords show error

## Files to Modify

| File | Changes |
|------|---------|
| `src/carry_on/api/pin_security.py` | Add `is_password_compliant()`, rename functions, update models |
| `src/carry_on/api/index.py` | Modify login, add `/api/update-password`, rename header param |
| `src/carry_on/static/index.html` | Update labels, inputs, add update step, update JS |
| `tests/test_pin_security.py` | Rename to `test_password_security.py`, add compliance tests |
| `tests/test_auth_api.py` | Add migration and update-password tests |
| `tests/acceptance/features/auth/*.feature` | Update terminology, add migration scenario |
| `tests/acceptance/pages/login_page.py` | Rename methods, add update password methods |

## Verification

1. Run unit tests: `nox -s tests_fast`
2. Run acceptance tests: `nox -s tests_acceptance`
3. Manual test:
   - Create user with weak PIN via direct DB insert
   - Login with weak PIN -> should see password update screen
   - Update to compliant password -> should proceed to app
   - Login again -> should go directly to app

## Backwards Compatibility

- `LoginRequest` keeps min_length=4 to allow existing users to log in
- Support both `X-Pin` and `X-Password` headers during transition
- Keep `pin_hash` DB field name (can migrate later)
