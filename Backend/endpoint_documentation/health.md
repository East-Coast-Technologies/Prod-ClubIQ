# Health API

This document covers the v1 backend health endpoint for ClubIQ.

## Base URL

```text
/api/v1/health/
```

## Auth

No authentication is required.

This endpoint is intended for:

```text
- uptime checks
- Docker health checks
- deployment validation
- monitoring systems
```

## Endpoints at a Glance

| # | Method | Endpoint | Description |
|---|---|---|---|
| 1 | GET | `/api/v1/health/` | Check backend availability |

## 1. Health Check

```http
GET /api/v1/health/
```

### Purpose

Confirms that the backend application is running and able to serve requests.

### Request Headers

None required.

### Success Response

Status:

```text
200 OK
```

Body:

```json
{
  "message": "It feels good up here"
}
```

### Common Errors

| Status | Meaning |
|---|---|
| 500 | Application startup or runtime failure |

## Production Notes

This endpoint should remain available even when:

```env
EXPOSE_LEGACY_API=false
SCHEDULER_API_ENABLED=false
```

The health endpoint is part of the v1 production route surface.

## Monitoring Example

```bash
curl http://localhost:5000/api/v1/health/
```

Expected output:

```json
{
  "message": "It feels good up here"
}
```

## Status Codes Quick Reference

| Status | Meaning |
|---|---|
| 200 | Backend is reachable |
| 500 | Backend is unhealthy |
