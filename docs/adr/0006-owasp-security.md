# ADR 0006: OWASP Security Best Practices

## Status

Accepted

## Context

CarryOn handles user data including golf statistics and potentially location data (GPS). As a web application with an API backend, we must protect against common security vulnerabilities to safeguard user data and maintain trust.

## Decision

We will follow **OWASP (Open Web Application Security Project)** best practices, specifically addressing the OWASP Top 10 vulnerabilities.

### OWASP Top 10 (2021) and our mitigations:

#### A01: Broken Access Control

**Risk**: Unauthorized access to data or functionality.

**Mitigations**:
- PIN-based authentication for all API endpoints
- Validate PIN on every request (not just session-based)
- Deny by default - require authentication unless explicitly public

#### A02: Cryptographic Failures

**Risk**: Exposure of sensitive data.

**Mitigations**:
- HTTPS only (enforced by Vercel)
- Environment variables for secrets (MONGODB_URI)
- User PINs hashed with Argon2id and stored in database (see ADR-0009)
- Never log sensitive data
- No secrets in git (use `.env` + `.gitignore`)

#### A03: Injection

**Risk**: SQL/NoSQL injection, command injection.

**Mitigations**:
- Use Pydantic models for input validation
- Use PyMongo's parameterized queries (not string concatenation)
- Validate and sanitize all user input

```python
# Good: Pydantic validates input
class ShotCreate(BaseModel):
    club: str
    distance: Optional[int] = Field(ge=0, le=400)
```

#### A04: Insecure Design

**Risk**: Missing security controls in design.

**Mitigations**:
- Threat modeling for new features
- Security requirements in ADRs
- Code review with security focus

#### A05: Security Misconfiguration

**Risk**: Insecure default configurations.

**Mitigations**:
- No debug mode in production
- Remove default credentials
- Disable unnecessary features/endpoints
- Keep dependencies updated

#### A06: Vulnerable and Outdated Components

**Risk**: Using components with known vulnerabilities.

**Mitigations**:
- Use `uv` lock file for reproducible builds
- Regular dependency updates
- Monitor for security advisories (GitHub Dependabot)

#### A07: Identification and Authentication Failures

**Risk**: Weak authentication mechanisms.

**Mitigations**:
- Email + PIN authentication required for all data access
- PINs hashed with Argon2id and stored per-user in database
- User isolation ensures users can only access their own data
- Rate limiting (future: implement for brute-force protection)

#### A08: Software and Data Integrity Failures

**Risk**: Unverified updates, CI/CD compromise.

**Mitigations**:
- Lock file (`uv.lock`) for dependency integrity
- GitHub branch protection (future)
- CI/CD pipeline security

#### A09: Security Logging and Monitoring Failures

**Risk**: Unable to detect breaches.

**Mitigations**:
- Log authentication failures
- Monitor for unusual patterns (future)
- Vercel provides request logging

#### A10: Server-Side Request Forgery (SSRF)

**Risk**: Server makes requests to unintended locations.

**Mitigations**:
- No user-controlled URLs in server requests
- Validate any external API calls

### Security checklist for new features:

- [ ] Input validation with Pydantic
- [ ] Authentication required
- [ ] No sensitive data in logs
- [ ] No secrets in code
- [ ] Dependencies scanned for vulnerabilities

## Consequences

### Positive

- Reduced risk of security breaches
- User data protected
- Industry-standard security practices
- Builds trust with users

### Negative

- Additional development overhead
- May slow down feature development
- Requires ongoing security awareness

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
