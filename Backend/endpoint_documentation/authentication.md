# Authentication API

<!--toc:start-->
- [Authentication API](#authentication-api)
  - [Base URL](#base-url)
  - [Used By](#used-by)
  - [Auth Model](#auth-model)
  - [Endpoints at a Glance](#endpoints-at-a-glance)
  - [Not Used in v1](#not-used-in-v1)
  - [1. Sync Current Clerk User](#1-sync-current-clerk-user)
    - [Purpose](#purpose)
    - [Request Headers](#request-headers)
    - [Request Body](#request-body)
    - [Important Rules](#important-rules)
    - [Success Response: Created](#success-response-created)
    - [Success Response: Updated](#success-response-updated)
    - [Common Errors](#common-errors)
  - [2. Get Current Auth Context](#2-get-current-auth-context)
    - [Purpose](#purpose-1)
    - [Request Headers](#request-headers-1)
    - [Success Response: User Is a Club Member](#success-response-user-is-a-club-member)
    - [Success Response: Synced User Is Not a Club Member](#success-response-synced-user-is-not-a-club-member)
    - [Important Access Note](#important-access-note)
    - [Common Errors](#common-errors-1)
  - [3. Test Auth Route](#3-test-auth-route)
    - [Purpose](#purpose-2)
    - [Request Headers](#request-headers-2)
    - [Success Response](#success-response)
    - [Common Errors](#common-errors-2)
  - [Frontend Example](#frontend-example)
  - [Production Notes](#production-notes)
  - [Status Codes Quick Reference](#status-codes-quick-reference)
<!--toc:end-->

This document covers the v1 backend authentication endpoints for ClubIQ.

## Base URL

```text
/api/v1/auth
```

## Used By

- Frontend contributors
- Backend maintainers
- API consumers
- QA/testing contributors

## Auth Model

ClubIQ uses Clerk for authentication.

The frontend signs the user in through Clerk, gets a Clerk session token, and sends that token to the Flask backend.

Every protected request must include:

```http
Authorization: Bearer <Clerk session token>
Content-Type: application/json
```

The backend verifies the Clerk token and loads the synced local user.

The frontend must not send `user_id` to identify the logged-in user. The backend resolves the current user from the verified Clerk token.

## Endpoints at a Glance

| # | Method | Endpoint | Description | Auth |
|---|---|---|---|---|
| 1 | POST | `/api/v1/auth/sync/` | Sync signed-in Clerk user into local DB | Required |
| 2 | GET | `/api/v1/auth/me` | Get current user, active club, membership, and access context | Required |
| 3 | GET | `/api/v1/auth/test/` | Test protected auth route | Required |

## Not Used in v1

The old user-id based profile route is not part of the v1 public contract:

```text
/api/v1/auth/me/<user_id>/
```

Use this instead:

```text
/api/v1/auth/me
```

## 1. Sync Current Clerk User

```http
POST /api/v1/auth/sync/
```

### Purpose

Creates or updates the authenticated Clerk user in the local ClubIQ database.

This endpoint is usually called after the user signs in.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
Content-Type: application/json
```

### Request Body

```json
{
  "email": "member@example.com",
  "name": "Club Member",
  "username": "clubmember",
  "role": "user"
}
```

### Important Rules

- The backend verifies the Clerk token.
- The backend gets `clerk_id` from the verified token.
- Client-supplied `clerk_id` is ignored.
- If the user does not exist locally, the backend creates the user.
- If the user already exists locally, the backend updates their profile fields.
- `email`, `name`, and `username` are required.
- `role` defaults to `user` unless provided.

### Success Response: Created

Status:

```text
200 OK
```

Body:

```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "clerk_id": "user_123",
    "name": "Club Member",
    "email": "member@example.com",
    "username": "clubmember",
    "role": "user",
    "created_at": "2026-01-01T09:45:11.089007",
    "updated_at": "2026-01-01T09:45:11.089007"
  },
  "verified_via": "Clerk"
}
```

### Success Response: Updated

Status:

```text
200 OK
```

Body:

```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "clerk_id": "user_123",
    "name": "Club Member",
    "email": "member@example.com",
    "username": "clubmember",
    "role": "user",
    "created_at": "2026-01-01T09:45:11.089007",
    "updated_at": "2026-01-01T10:12:48.901221"
  },
  "verified_via": "Clerk"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 400 | Missing required fields |
| 401 | Authorization token missing or invalid |
| 409 | Duplicate email, username, or Clerk ID conflict |
| 500 | Unexpected server error |

## 2. Get Current Auth Context

```http
GET /api/v1/auth/me
```

### Purpose

Returns the authenticated user's current application context.

This is the main v1 endpoint the frontend should call after sync.

It returns:

```text
- current local user
- configured active club
- current membership in that club
- access information
```

### Request Headers

```http
Authorization: Bearer <Clerk session token>
```

### Success Response: User Is a Club Member

Status:

```text
200 OK
```

Body:

```json
{
  "user": {
    "id": 1,
    "clerk_id": "user_123",
    "name": "Club Member",
    "email": "member@example.com",
    "username": "clubmember",
    "role": "user",
    "created_at": "2026-01-01T09:45:11.089007",
    "updated_at": "2026-01-01T10:12:48.901221"
  },
  "club": {
    "id": "2e1fefb4-8a32-421b-8eb3-16ff105fd972",
    "name": "clubIQ",
    "description": "Main production club"
  },
  "member": {
    "id": "8c59e72b-b56d-4e49-bdb3-1763bb3ddc56",
    "club_id": "2e1fefb4-8a32-421b-8eb3-16ff105fd972",
    "user_id": 1,
    "username": "clubmember",
    "role": "member",
    "joined_at": "2026-01-01T10:20:11.240421"
  },
  "access": {
    "is_member": true,
    "role": "member"
  }
}
```

### Success Response: Synced User Is Not a Club Member

Status:

```text
200 OK
```

Body:

```json
{
  "user": {
    "id": 2,
    "clerk_id": "user_456",
    "name": "Non Member",
    "email": "nonmember@example.com",
    "username": "nonmember",
    "role": "user",
    "created_at": "2026-01-01T09:45:11.089007",
    "updated_at": "2026-01-01T10:12:48.901221"
  },
  "club": {
    "id": "2e1fefb4-8a32-421b-8eb3-16ff105fd972",
    "name": "clubIQ",
    "description": "Main production club"
  },
  "member": null,
  "access": {
    "is_member": false,
    "role": null
  }
}
```

### Important Access Note

A synced user who is not a member can call `/api/v1/auth/me` to see their status.

But they cannot access protected club data such as:

```text
/api/v1/activities/
/api/v1/members/
```

Those endpoints return `403` when the synced user is not allowed inside the configured club.

### Common Errors

| Status | Meaning |
|---|---|
| 401 | Authorization token missing or invalid |
| 403 | Clerk user is authenticated but not synced in local DB |
| 404 | Configured club was not found |
| 500 | `SINGLE_CLUB_NAME` is missing or unexpected server error |

## 3. Test Auth Route

```http
GET /api/v1/auth/test/
```

### Purpose

Simple protected route used to confirm that auth middleware works.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
```

### Success Response

Status:

```text
200 OK
```

Body:

```json
{
  "message": "Hello, clubmember!"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 401 | Authorization token missing or invalid |
| 403 | User is not synced locally |

## Frontend Example

Example flow:

```text
1. User signs in with Clerk
2. Frontend gets Clerk session token
3. Frontend calls POST /api/v1/auth/sync/
4. Frontend calls GET /api/v1/auth/me
5. Frontend uses the returned access context to decide what to show
```

Example fetch:

```typescript
const token = await getToken();

const response = await fetch("http://127.0.0.1:5000/api/v1/auth/me", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

const data = await response.json();
console.log(data);
```

## Production Notes

Required backend env values:

```env
CLERK_SECRET_KEY=<production-clerk-secret>
CLERK_ISSUER=<production-clerk-issuer>
CLERK_JWKS_URL=<production-clerk-jwks-url>
SINGLE_CLUB_NAME=<real-production-club-name>
```

Production should also use:

```env
EXPOSE_LEGACY_API=false
SCHEDULER_API_ENABLED=false
FLASK_DEBUG=false
```

## Status Codes Quick Reference

| Status | Meaning |
|---|---|
| 200 | Successful sync, auth context read, or test response |
| 400 | Bad request body |
| 401 | Missing or invalid auth token |
| 403 | Authenticated but not synced or not allowed |
| 404 | Configured club not found |
| 409 | Duplicate local user constraint |
| 500 | Server/configuration error |
