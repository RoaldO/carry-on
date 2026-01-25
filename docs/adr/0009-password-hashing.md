# ADR 0009: Password Hashing with Argon2id

## Status

Accepted

## Context

CarryOn stores user PINs for authentication. Initially, PINs were stored as plain text for simplicity during early development. This poses a security risk: if the database is compromised, all user credentials are immediately exposed.

We need a secure password hashing solution that:
- Protects credentials even if the database is leaked
- Supports migration from plain text without disrupting existing users
- Allows future algorithm upgrades as cryptographic best practices evolve

## Decision

We will use **Argon2id** for password hashing via the `argon2-cffi` library. This is **mandatory** for all credential storage.

### Why Argon2id?

- **Winner of the Password Hashing Competition (2015)** - peer-reviewed and vetted by cryptographers
- **Memory-hard** - resistant to GPU/ASIC attacks unlike bcrypt or PBKDF2
- **Argon2id variant** - combines Argon2i (side-channel resistant) and Argon2d (GPU-resistant)
- **OWASP recommended** for new applications
- **Self-describing format** - PHC string format includes algorithm and parameters

### Storage Format

Hashes use the PHC (Password Hashing Competition) string format:

```
$argon2id$v=19$m=65536,t=3,p=4$<base64-salt>$<base64-hash>
```

This format is self-describing:
- `$argon2id$` - algorithm identifier
- `v=19` - Argon2 version
- `m=65536,t=3,p=4` - memory cost, time cost, parallelism
- Salt and hash are base64-encoded

### Migration Strategy

The system supports transparent migration from plain text to hashed PINs:

1. **Detection**: Check if stored value starts with `$argon2`
   - Yes: Verify using Argon2
   - No: Verify as plain text (legacy)

2. **Rehashing on login**: After successful authentication with a plain text PIN:
   - Hash the PIN with Argon2id
   - Update the database with the new hash

3. **New registrations**: Always hash with Argon2id

```python
def verify_pin(pin: str, stored_hash: str) -> bool:
    if stored_hash.startswith("$argon2"):
        return argon2_verify(stored_hash, pin)
    else:
        return stored_hash == pin  # Legacy plain text

def needs_rehash(stored_hash: str) -> bool:
    if not stored_hash.startswith("$argon2"):
        return True  # Plain text needs hashing
    return hasher.check_needs_rehash(stored_hash)  # Outdated params
```

### Future Algorithm Upgrades

The same pattern supports future algorithm changes:

1. Add detection for new algorithm prefix
2. Verify using appropriate algorithm
3. Rehash to current preferred algorithm on successful login

For example, if Argon2id is superseded by "Argon3" in the future:

```python
def verify_pin(pin: str, stored_hash: str) -> bool:
    if stored_hash.startswith("$argon3"):
        return argon3_verify(stored_hash, pin)
    elif stored_hash.startswith("$argon2"):
        return argon2_verify(stored_hash, pin)
    else:
        return stored_hash == pin
```

### Implementation Requirements

**Mandatory rules**:
- Never store plain text passwords/PINs in new code
- Always use `hash_pin()` before storing credentials
- Always use `verify_pin()` for authentication (never direct comparison)
- Always check `needs_rehash()` after successful authentication
- Never log or expose password hashes

**Library usage**:
```python
from api.pin_security import hash_pin, verify_pin, needs_rehash

# Storing new credential
stored_hash = hash_pin(user_pin)

# Verifying credential
if verify_pin(user_pin, stored_hash):
    if needs_rehash(stored_hash):
        new_hash = hash_pin(user_pin)
        update_user_hash(new_hash)
```

## Consequences

### Positive

- **Secure storage**: Credentials protected even if database is compromised
- **Zero-downtime migration**: Existing users upgraded transparently
- **Future-proof**: Algorithm upgrades without mass password resets
- **Industry standard**: Following OWASP and cryptographic best practices
- **Audit trail**: Hash format indicates which algorithm was used

### Negative

- **Computational cost**: Argon2 is intentionally slow (~100ms per hash)
- **Memory usage**: Default parameters use 64MB per hash operation
- **Dependency**: Requires `argon2-cffi` library with native bindings
- **Complexity**: Migration logic adds code paths to maintain

### Mitigations

- Computational cost is acceptable for authentication (not high-frequency)
- Memory usage is brief and acceptable for serverless
- Library is well-maintained and widely used

## References

- [Argon2 RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [argon2-cffi documentation](https://argon2-cffi.readthedocs.io/)
- [Password Hashing Competition](https://www.password-hashing.net/)
