# Club API

This document covers the v1 backend club endpoint for ClubIQ.

## Base URL

```text
/api/v1/club
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
| 1 | GET | `/api/v1/club/` | Get the configured active club | Required |

## Not Used in v1

These old multi-club route patterns are not part of the v1 public contract:

```text
/api/v1/clubs/
/api/v1/clubs/<club_id>
```

v1 does not expose public multi-club CRUD.

Multi-club management is reserved for v2.

## 1. Get Active Club

```http
GET /api/v1/club/
```

### Purpose

Returns the configured single active club for v1.

This endpoint lets the frontend know which club the v1 backend is currently serving.

### Request Headers

```http
Authorization: Bearer <Clerk session token>
```

### Behavior

- Backend reads `SINGLE_CLUB_NAME`.
- Backend finds the matching club in the database.
- Backend returns that club.
- The frontend does not send `club_id`.

### Success Response

Status:

```text
200 OK
```

Body:

```json
{
  "id": "e58b9984-ebfc-4308-9223-69944ece8c09",
  "name": "clubIQ",
  "description": "Main production club"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 401 | Authorization token missing or invalid |
| 403 | User is authenticated but not synced locally |
| 404 | Configured club was not found |
| 500 | `SINGLE_CLUB_NAME` is missing or unexpected server error |

## Production Notes

The production club is controlled by:

```env
SINGLE_CLUB_NAME=<real-production-club-name>
```

Before production deployment, make sure the database contains a club with the same name.

Example:

```env
SINGLE_CLUB_NAME=clubIQ
```

The value must match the `clubs.name` value in the database.

## v2 Notes

v2 can reintroduce multi-club APIs using a separate versioned route surface, for example:

```text
/api/v2/clubs/
/api/v2/clubs/<club_id>
```

Do not add multi-club behavior back into `/api/v1`.

## Status Codes Quick Reference

| Status | Meaning |
|---|---|
| 200 | Configured club returned successfully |
| 401 | Missing or invalid auth token |
| 403 | Authenticated but not synced |
| 404 | Configured club not found |
| 500 | Server/configuration error |
