# Credential / Auth Module

## Overview

Handles all authentication and account management — login, signup, JWT token lifecycle, password reset, and OAuth provider auth.

---

## Routes (`AuthServer`)

No rate limiting is currently active (commented out). All routes are public unless noted.

| Method | Endpoint | Handler |
|--------|----------|---------|
| `POST` | `/login` | `login` |
| `POST` | `/signup` | `signup` |
| `POST` | `/verify-code` | `verify_code` |
| `POST` | `/login-via-token` | `login_via_token` |
| `POST` | `/request-access-token` | `request_new_access_token` |
| `POST` | `/provider/<provider>` | `provider_verify` |
| `POST` | `/provider/complete-signup` | `singup_provider` |
| `POST` | `/reset-password` | `request_reset_password` |
| `POST` | `/reset-password/verify` | `request_reset_password_verify` |
| `POST` | `/reset-password/reset` | `request_reset_password_complete` |

---

### `POST /login`

Standard email/password or username/password login.

**Request Body**
```json
{
  "username": "string | null",
  "email": "string | null",
  "password": "string"
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ message, user_data: { user_id, role }, tokens }` |
| `401` | Wrong username/email |
| `403` | Wrong password |
| `400` | Input validation failed |
| `500` | Server error |

---

### `POST /signup`

Register a new account. Sends a 6-digit OTP to the email.

**Request Body**
```json
{
  "email": "string",
  "displayName": "string",
  "username": "string",
  "password": "string"
}
```

**Response**

| Code | Body |
|------|------|
| `201` | `{ code: "pending" }` — OTP sent |
| `400` | Email or username already in use |
| `400` | Input validation failed |
| `500` | Failed to send OTP |

Pending user data (hashed password + fields) is stored in Redis for 300 seconds, keyed by OTP code.

---

### `POST /verify-code`

Confirm the OTP from signup to complete account creation.

**Request Body**
```json
{
  "email": "string",
  "code": "number"
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Invalid or expired code |
| `500` | DB insert failed |

On success, clears both Redis keys (email key + code key) and inserts the user into PostgreSQL.

---

### `POST /login-via-token`

Validate an access JWT and return user data. Used on app launch to restore session.

**Headers**
- `Authorization: Bearer <access_token>`

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully", user_data: { user_id, role } }` |
| `401` | Invalid or expired token |
| `500` | Server error |

---

### `POST /request-access-token`

Exchange a valid refresh token for a new access token.

**Headers**
- `Authorization: Bearer <refresh_token>`

**Response**

| Code | Body |
|------|------|
| `200` | `{ message, token: <new_access_token> }` |
| `401` | Token expired or not in DB |
| `404` | Missing token or server error |

Verifies the refresh token is both valid (JWT check) and registered in the DB.

---

### `POST /provider/<provider>`

Verify an OAuth ID token from a provider (currently only `google`). Handles both login and signup flows.

**Request Body**
```json
{ "id_token": "string" }
```

**Response — existing user (login)**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully", tokens, user_data }` |
| `400` | Account not linked to this provider |

**Response — new user (signup needed)**

| Code | Body |
|------|------|
| `201` | `{ code: "pending", pending_token }` — redirect to complete signup |
| `400` | Provider data fetch failed |

Google tokens are tried against both `GOOGLE_CLIENT_ID` (web) and `IOS_CLIENT_ID` environment variables.

---

### `POST /provider/complete-signup`

Complete OAuth signup by supplying a username, display name, and password.

**Request Body**
```json
{
  "pending_token": "string",
  "username": "string",
  "display_name": "string",
  "password": "string"
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Token expired, email or username taken, validation failed |
| `500` | DB insert failed |

`pending_token` links back to the Redis entry created in `/provider/<provider>` (TTL 300s).

---

### `POST /reset-password`

Phase 1 — request a password reset. Sends a 6-digit OTP to the email.

**Request Body**
```json
{ "email": "string" }
```

**Response**

| Code | Body |
|------|------|
| `201` | `{ code: "pending" }` |
| `404` | Email not found |
| `500` | Failed to send OTP |

OTP stored in Redis for 300 seconds.

---

### `POST /reset-password/verify`

Phase 2 — verify the OTP. Returns a short-lived token to authorize the actual reset.

**Request Body**
```json
{
  "email": "string",
  "code": "number"
}
```

**Response**

| Code | Body |
|------|------|
| `201` | `{ code: "verified", token }` |
| `400` | Wrong code or email mismatch |
| `500` | Server error |

On success, deletes the OTP key and stores the verified token in Redis (300s TTL).

---

### `POST /reset-password/reset`

Phase 3 — set a new password using the verified token.

**Request Body**
```json
{
  "email": "string",
  "token": "string",
  "new_password": "string"
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Invalid token or email mismatch |
| `500` | DB update failed |

Validates new password, hashes it, updates the DB, deletes the token from Redis, and writes an audit log entry.

---

## Services

### `LoginService`

Singleton. Looks up user by username or email, verifies bcrypt password hash, then calls `_jwt_cycle_handler` to generate access + refresh tokens.

---

### `SignupService`

Singleton. Two-step process:

1. `signup()` — validates inputs, checks for duplicate email/username, sends OTP, stores pending user data in Redis.
2. `confirm_code_and_process_new_user()` — verifies OTP, calls `process_new_user()` to insert into PostgreSQL, cleans up Redis.

---

### `JWTAuthenticationService`

Singleton. Two methods:

- `login_via_token(token)` — verifies JWT, decodes `user_id` and `role`, returns user data.
- `request_new_access_token(refresh_token)` — verifies JWT validity + DB presence, issues a new access token.

---

### `ResetPasswordService`

Singleton. Three-phase flow using Redis as a state machine:

| Phase | Redis Key | TTL |
|-------|-----------|-----|
| OTP sent | `reset_password:code:<code>` | 300s |
| OTP verified | `reset_password:token:<uuid>` | 300s |

Phase 3 writes an audit log via `UserdataAudit._update_user_audit` with `action="reset_password"`, storing old and new hashed passwords.

---

### `ProviderAuth`

Singleton. Handles Google OAuth:

- `provider_verify()` — verifies Google `id_token`, checks if user exists. Returns tokens on login or a `pending_token` for new users.
- `provider_signup_complete()` — uses `pending_token` to retrieve cached provider data, then inserts the full user record.
- `_provider_verification_google()` — tries both `GOOGLE_CLIENT_ID` and `IOS_CLIENT_ID` to verify the token.

Pending provider data stored in Redis as `new_user_pending_provider:token:<uuid>` (TTL 300s).

---

## Notes

- All password hashing uses `werkzeug.security` (`generate_password_hash` / `check_password_hash`)
- Email is lowercased before all DB lookups
- JWT cycle (access + refresh token generation) is handled by `_jwt_cycle_handler` in `CredentialBase`
- Rate limiter is implemented but currently commented out (5 req/min per IP via Redis `incr` + `expire`)
- Provider support is currently Google only; other providers return `400`
