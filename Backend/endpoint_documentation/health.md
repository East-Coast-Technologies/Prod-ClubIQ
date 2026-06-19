# Health API

<!--toc:start-->
- [Health API](#health-api)
  - [Base URL](#base-url)
  - [Auth](#auth)
  - [Endpoints at a Glance](#endpoints-at-a-glance)
  - [Response](#response)
    - [Purpose](#purpose)
    - [Request Headers](#request-headers)
    - [Common Errors](#common-errors)
  - [Production Notes](#production-notes)
  - [Monitoring Examples](#monitoring-examples)
  - [Status Codes Quick Reference](#status-codes-quick-reference)
<!--toc:end-->

This document covers backend health and liveness endpoints for ClubIQ.

## Base URL

```text
/api/v1/health/
```

## Auth

No authentication is required.

These endpoints are intended for:

```text
- uptime checks
- Docker Compose health checks
- deployment validation
- monitoring systems
```

## Endpoints at a Glance

| # | Method | Endpoint | Availability | Description |
|---|---|---|---|---|
| 1 | GET | `/api/v1/health` and `/api/v1/health/` | Always | v1 public health check |
| 2 | GET | `/api/health` and `/api/health/` | Only when `EXPOSE_LEGACY_API=true` | Legacy health check |
| 3 | GET | `/backend-health`, `/backend-health/`, `/api/backend-health`, `/api/backend-health/` | Always | Docker/backend liveness probe routes |

## Response

All health endpoints return:

Status:

```text
200 OK
```

Body:

```json
{
  "status": "healthy",
  "message": "It feels good up here"
}
```

### Purpose

Confirms that the backend application is running and able to serve requests.

### Request Headers

None required.

### Common Errors

| Status | Meaning |
|---|---|
| 500 | Application startup or runtime failure |

## Production Notes

In production:

```env
EXPOSE_LEGACY_API=false
SCHEDULER_API_ENABLED=false
```

With that configuration:

- `/api/health...` (legacy) is not exposed.
- `/api/v1/health...` remains exposed.
- Docker liveness routes (`/api/backend-health...`, `/backend-health...`) remain exposed.

## Monitoring Examples

```bash
curl http://localhost:5000/api/v1/health/
curl http://localhost:5000/api/backend-health
```

Expected output:

```json
{
  "status": "healthy",
  "message": "It feels good up here"
}
```

## Status Codes Quick Reference

| Status | Meaning |
|---|---|
| 200 | Backend is reachable |
| 500 | Backend is unhealthy |
