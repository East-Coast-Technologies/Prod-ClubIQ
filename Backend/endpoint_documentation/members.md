# Members API

This document covers the v1 backend members endpoints for ClubIQ.

## Base URL

```text
/api/v1/members
```

## Auth

All endpoints require a valid Clerk session token.

```http
Authorization: Bearer <Clerk session token>
Content-Type: application/json
```

The backend verifies the Clerk token and loads the synced local user.

## v1 Single-Club Rule

v1 is single-club only.

The frontend must not send `club_id`.

The backend resolves the active club using:

```env
SINGLE_CLUB_NAME=<club-name>
```

## Endpoints at a Glance

| # | Method | Endpoint | Description | Auth |
|---|---|---|---|---|
| 1 | GET | `/api/v1/members/` | List members in the configured club | Required |
| 2 | POST | `/api/v1/members/` | Create a member in the configured club | Required |
| 3 | GET | `/api/v1/members/<member_id>` | Get one member from the configured club | Required |
| 4 | PUT | `/api/v1/members/<member_id>` | Update one member from the configured club | Required |
| 5 | DELETE | `/api/v1/members/<member_id>` | Delete one member from the configured club | Required |

## Not Used in v1

These old multi-club patterns are not part of the v1 public contract:

```text
/api/v1/members/?club_id=<club_id>
```

These request body patterns are rejected in v1:

```json
{
  "club_id": "client-provided-club-id"
}
```

If `club_id` is sent in a v1 create or update request body, the backend returns `400`.

If `club_id` is sent as a query param to the v1 list endpoint, the backend returns `400`.

## Access Control

A synced user can access v1 members only if they are allowed inside the configured club.

Allowed users:

```text
- member of the configured club
- creator of the configured club
- admin
- super_user
```

Blocked users:

```text
- synced but not a member of the configured club
- unsynced Clerk user
```

Blocked users receive `403`.

## IDs

| ID | Type | Notes |
|---|---|---|
| `member_id` | UUID string | Membership record id |
| `user_id` | integer | Local synced user id |
| `club_id` | UUID string | Returned in responses, but not accepted from frontend in v1 |

## 1. List Members

```http
GET /api/v1/members/
```

### Purpose

Returns members for the configured v1 club.

The frontend does not provide a `club_id`.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
```

### Query Params

| Query Param | Type | Required | Notes |
|---|---|---|---|
| `mine` | boolean | No | Optional. Keeps support for current filtering behavior. |
| `club_id` | UUID | No | Rejected in v1. Do not send. |

### Behavior

- Backend reads `SINGLE_CLUB_NAME`.
- Backend finds the configured club.
- Backend checks that the synced user can access that club.
- Backend returns members for that club only.
- If `club_id` query param is sent, backend returns `400`.

### Success Response

Status:

```text
200 OK
```

Body:

```json
[
  {
    "id": "73a799b1-f4c1-4cfd-acf8-2866e480462c",
    "club_id": "e58b9984-ebfc-4308-9223-69944ece8c09",
    "user_id": 5,
    "username": "alice",
    "role": "member",
    "joined_at": "2026-01-02T10:00:00"
  }
]
```

### Error: Client Sends `club_id` Query Param

Status:

```text
400 Bad Request
```

Body:

```json
{
  "error": "club_id query param is not accepted in v1"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 400 | `club_id` query param was sent |
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot access the configured club |
| 404 | Configured club was not found |
| 500 | `SINGLE_CLUB_NAME` is missing or unexpected server error |

## 2. Create Member

```http
POST /api/v1/members/
```

### Purpose

Creates a membership under the configured v1 club.

The frontend does not send `club_id`.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
Content-Type: application/json
```

### Request Body

```json
{
  "user_id": 5,
  "role": "member"
}
```

### Required Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | integer | Yes | Local synced user id to add to the club |
| `role` | string | No | Defaults to `member` when omitted |

### Rejected Fields

| Field | Reason |
|---|---|
| `club_id` | v1 resolves the active club from backend config |

### Behavior

- Backend reads `SINGLE_CLUB_NAME`.
- Backend finds the configured club.
- Backend injects the configured club id internally.
- Backend creates the membership under that club.
- Duplicate membership is rejected.

### Success Response

Status:

```text
201 Created
```

Body:

```json
{
  "message": "Member created successfully",
  "id": "73a799b1-f4c1-4cfd-acf8-2866e480462c",
  "club_id": "e58b9984-ebfc-4308-9223-69944ece8c09",
  "user_id": 5,
  "username": "alice",
  "role": "member",
  "joined_at": "2026-01-02T10:00:00"
}
```

### Error: Client Sends `club_id`

Status:

```text
400 Bad Request
```

Body:

```json
{
  "error": "club_id is not accepted in v1"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 400 | Missing required fields, duplicate membership, invalid user, or `club_id` was sent |
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot create members in the configured club |
| 404 | Configured club or target user was not found |
| 409 | Database constraint issue |
| 500 | `SINGLE_CLUB_NAME` is missing or unexpected server error |

## 3. Get Member by ID

```http
GET /api/v1/members/<member_id>
```

### Purpose

Returns one membership from the configured v1 club.

The requested `member_id` must belong to the configured club.

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
  "id": "73a799b1-f4c1-4cfd-acf8-2866e480462c",
  "club_id": "e58b9984-ebfc-4308-9223-69944ece8c09",
  "user_id": 5,
  "username": "alice",
  "role": "member",
  "joined_at": "2026-01-02T10:00:00"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot access the configured club |
| 404 | Member was not found in the configured club |
| 500 | Server/configuration error |

## 4. Update Member

```http
PUT /api/v1/members/<member_id>
```

### Purpose

Updates one membership from the configured v1 club.

The requested `member_id` must belong to the configured club.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
Content-Type: application/json
```

### Request Body

```json
{
  "role": "moderator"
}
```

### Allowed Fields

| Field | Type | Notes |
|---|---|---|
| `role` | string | Membership role |

### Rejected Fields

| Field | Reason |
|---|---|
| `club_id` | v1 resolves the active club from backend config |

### Success Response

Status:

```text
200 OK
```

Body:

```json
{
  "message": "Member updated successfully",
  "id": "73a799b1-f4c1-4cfd-acf8-2866e480462c",
  "club_id": "e58b9984-ebfc-4308-9223-69944ece8c09",
  "user_id": 5,
  "username": "alice",
  "role": "moderator",
  "joined_at": "2026-01-02T10:00:00"
}
```

### Error: Client Sends `club_id`

Status:

```text
400 Bad Request
```

Body:

```json
{
  "error": "club_id is not accepted in v1"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 400 | Invalid request body or `club_id` was sent |
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot update members in the configured club |
| 404 | Member was not found in the configured club |
| 409 | Database constraint issue |
| 500 | Server/configuration error |

## 5. Delete Member

```http
DELETE /api/v1/members/<member_id>
```

### Purpose

Deletes one membership from the configured v1 club.

The requested `member_id` must belong to the configured club.

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
  "message": "Member deleted successfully"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot delete members in the configured club |
| 404 | Member was not found in the configured club |
| 409 | Database constraint issue |
| 500 | Server/configuration error |

## Frontend Example: List Members

```typescript
const token = await getToken();

const response = await fetch("http://127.0.0.1:5000/api/v1/members/", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

const data = await response.json();
console.log(data);
```

## Frontend Example: Create Member

```typescript
const token = await getToken();

const response = await fetch("http://127.0.0.1:5000/api/v1/members/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    user_id: 5,
    role: "member",
  }),
});

const data = await response.json();
console.log(data);
```

## Status Codes Quick Reference

| Status | Meaning |
|---|---|
| 200 | Members returned, member returned, member updated, or member deleted |
| 201 | Member created successfully |
| 400 | Bad request body, duplicate membership, rejected `club_id`, or invalid input |
| 401 | Missing or invalid auth token |
| 403 | Authenticated but not synced or not allowed |
| 404 | Configured club, target user, or member not found |
| 409 | Database constraint issue |
| 500 | Server/configuration error |
