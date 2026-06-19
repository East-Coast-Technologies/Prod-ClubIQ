# Invitations API

<!--toc:start-->
- [Invitations API](#invitations-api)
  - [v1 Status](#v1-status)
  - [Not Exposed in v1](#not-exposed-in-v1)
  - [Legacy Routes](#legacy-routes)
  - [v1 Invitation Flow](#v1-invitation-flow)
  - [Backend Responsibility](#backend-responsibility)
  - [Related v1 Endpoints](#related-v1-endpoints)
  - [Expected Access Behavior](#expected-access-behavior)
  - [Production Notes](#production-notes)
  - [v2 Notes](#v2-notes)
  - [Status Codes Quick Reference](#status-codes-quick-reference)
<!--toc:end-->

This document covers the v1 backend invitation decision for ClubIQ.

## v1 Status

ClubIQ v1 does not expose local backend invitation endpoints.

Invitation and sign-up access should be handled by Clerk.

The Flask backend is responsible for:

```text
- verifying Clerk authentication
- syncing authenticated Clerk users into the local database
- checking whether a synced user belongs to the configured club
- blocking users who are not allowed to access v1 club data
```

## Not Exposed in v1

These routes are intentionally not part of the v1 production API:

```text
/api/v1/invitations/
/api/v1/invitations/<invite_id>
/api/v1/invitations/<token>/accept
```

Do not build new v1 invitation endpoints in Flask.

Do not expose the legacy invitation system under `/api/v1`.

## Legacy Routes

The legacy backend may still contain old invitation routes under:

```text
/api/invitations/
```

Those routes are not part of the v1 production API contract.

In production, legacy APIs should be disabled with:

```env
EXPOSE_LEGACY_API=false
```

When legacy APIs are disabled, `/api/invitations/` is not exposed.

## v1 Invitation Flow

The v1 invitation flow should work like this:

```text
1. Admin/team owner invites the user through Clerk.
2. Clerk sends the invitation or sign-up access link.
3. User signs up or signs in through Clerk.
4. Frontend gets a Clerk session token.
5. Frontend calls POST /api/v1/auth/sync/.
6. Backend syncs the authenticated Clerk user into the local database.
7. Frontend calls GET /api/v1/auth/me.
8. Backend returns the user's club membership/access context.
9. If the user is a member of the configured club, they can access v1 club data.
10. If the user is not a member of the configured club, protected club data endpoints return 403.
```

## Backend Responsibility

The backend does not decide who receives Clerk invitations in v1.

The backend only decides whether the authenticated and synced user can access the configured club.

Allowed users:

```text
- member of the configured club
- creator of the configured club
- admin
- super_user
```

Blocked users:

```text
- unsynced Clerk user
- synced user who is not allowed inside the configured club
```

## Related v1 Endpoints

Use these endpoints for the v1 auth and access flow:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/sync/` | Sync the signed-in Clerk user into the local DB |
| GET | `/api/v1/auth/me` | Return current user, configured club, membership, and access context |
| GET | `/api/v1/club/` | Return the configured single club |

## Expected Access Behavior

A synced user who is not a member can call:

```text
/api/v1/auth/me
```

That endpoint returns:

```json
{
  "member": null,
  "access": {
    "is_member": false,
    "role": null
  }
}
```

But the same user cannot access protected club data endpoints such as:

```text
/api/v1/activities/
/api/v1/members/
```

Those endpoints return:

```text
403 Forbidden
```

## Production Notes

Production should use:

```env
EXPOSE_LEGACY_API=false
SCHEDULER_API_ENABLED=false
SINGLE_CLUB_NAME=<real-production-club-name>
```

Before production deployment:

```text
- confirm Clerk invitation/sign-up settings are configured
- confirm the production club exists in the database
- confirm SINGLE_CLUB_NAME matches the production club name
- confirm users who should access the club have membership records
- confirm /api/v1/invitations routes are not exposed
```

## v2 Notes

If ClubIQ v2 reintroduces multi-club behavior, invitations can be redesigned under a v2 route surface, for example:

```text
/api/v2/invitations/
/api/v2/clubs/<club_id>/invitations/
```

Do not add local invitation behavior back into `/api/v1`.

## Status Codes Quick Reference

Because v1 does not expose invitation endpoints, there are no v1 invitation status codes.

Expected route behavior:

| Route | Expected Status |
|---|---|
| `/api/v1/invitations/` | 404 Not Found |
| `/api/v1/invitations/<invite_id>` | 404 Not Found |
| `/api/v1/invitations/<token>/accept` | 404 Not Found |
