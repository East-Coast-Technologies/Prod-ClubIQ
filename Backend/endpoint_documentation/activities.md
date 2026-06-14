# Activities API

This document covers the v1 backend activities endpoints for ClubIQ.

## Base URL

```text
/api/v1/activities
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
| 1 | GET | `/api/v1/activities/` | List activities for the configured club | Required |
| 2 | POST | `/api/v1/activities/` | Create an activity in the configured club | Required |

## Not Used in v1

These old multi-club route patterns are not part of the v1 public contract:

```text
/api/v1/activities/create/
/api/v1/activities/<club_id>/
```

These request patterns are also rejected in v1:

```json
{
  "club_id": "client-provided-club-id"
}
```

If `club_id` is sent in the v1 create request body, the backend returns `400`.

## Access Control

A synced user can access v1 activities only if they are allowed inside the configured club.

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

## 1. List Activities

```http
GET /api/v1/activities/
```

### Purpose

Returns activities for the configured v1 club.

The frontend does not provide a `club_id`.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
```

### Behavior

- Backend reads `SINGLE_CLUB_NAME`.
- Backend finds the configured club.
- Backend checks that the synced user can access that club.
- Backend returns activities for that club only.
- Activities are ordered by `created_at` descending.

### Success Response

Status:

```text
200 OK
```

Body:

```json
[
  {
    "id": "d7f9c3b4-4a59-49aa-942a-62fd69439c89",
    "club_id": "e58b9984-ebfc-4308-9223-69944ece8c09",
    "title": "Movie Night",
    "description": "Watch films together",
    "start_date": "2026-01-02T19:20:00",
    "end_date": null,
    "author_id": 1,
    "created_at": "2026-01-02T19:20:00"
  }
]
```

### Common Errors

| Status | Meaning |
|---|---|
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot access the configured club |
| 404 | Configured club was not found |
| 500 | `SINGLE_CLUB_NAME` is missing or unexpected server error |

## 2. Create Activity

```http
POST /api/v1/activities/
```

### Purpose

Creates an activity under the configured v1 club.

The frontend does not send `club_id`.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
Content-Type: application/json
```

### Request Body

```json
{
  "title": "Movie Night",
  "description": "Watch films together"
}
```

### Required Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Yes | Activity title |
| `description` | string | No | Optional description |

### Rejected Fields

| Field | Reason |
|---|---|
| `club_id` | v1 resolves the active club from backend config |

### Behavior

- Backend reads `SINGLE_CLUB_NAME`.
- Backend finds the configured club.
- Backend injects the configured club id internally.
- Backend creates the activity under that club.
- Duplicate activity titles in the same club are rejected.

### Success Response

Status:

```text
201 Created
```

Body:

```json
{
  "message": "Activity created successfully",
  "Details": {
    "id": "d7f9c3b4-4a59-49aa-942a-62fd69439c89",
    "club_id": "e58b9984-ebfc-4308-9223-69944ece8c09",
    "title": "Movie Night",
    "description": "Watch films together",
    "start_date": "2026-01-02T19:20:00",
    "end_date": null,
    "author_id": 1,
    "created_at": "2026-01-02T19:20:00"
  }
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
  "message": "club_id is not accepted in v1"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 400 | Missing title, duplicate title, or `club_id` was sent |
| 401 | Authorization token missing or invalid |
| 403 | User is not synced or cannot create activity in the configured club |
| 404 | Configured club was not found |
| 409 | Database constraint error |
| 500 | `SINGLE_CLUB_NAME` is missing or unexpected server error |

## Frontend Example

```typescript
const token = await getToken();

const response = await fetch("http://127.0.0.1:5000/api/v1/activities/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "Movie Night",
    description: "Watch films together",
  }),
});

const data = await response.json();
console.log(data);
```

## Status Codes Quick Reference

| Status | Meaning |
|---|---|
| 200 | Activities returned successfully |
| 201 | Activity created successfully |
| 400 | Bad request body or rejected `club_id` |
| 401 | Missing or invalid auth token |
| 403 | Authenticated but not synced or not allowed |
| 404 | Configured club not found |
| 409 | Database constraint issue |
| 500 | Server/configuration error |
