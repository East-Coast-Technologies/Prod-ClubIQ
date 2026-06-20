# Contributing to ClubIQ

<!--toc:start-->
- [Contributing to ClubIQ](#contributing-to-clubiq)
  - [Project Structure](#project-structure)
  - [Development Rules](#development-rules)
  - [Branch Naming](#branch-naming)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup](#docker-setup)
  - [Backend Contribution Guidelines](#backend-contribution-guidelines)
  - [API Versioning Rules](#api-versioning-rules)
  - [Backend Testing](#backend-testing)
  - [Database and Migrations](#database-and-migrations)
  - [Authentication Rules](#authentication-rules)
  - [Pull Request Checklist](#pull-request-checklist)
  - [Commit Message Style](#commit-message-style)
  - [Code Review Expectations](#code-review-expectations)
  - [Documentation](#documentation)
  - [Security](#security)
  - [Reporting Issues](#reporting-issues)
  - [Production Focus](#production-focus)
<!--toc:end-->

Thanks for your interest in contributing to ClubIQ.

ClubIQ is a smart club management system built as a monorepo with a Flask backend and a Next.js frontend.

The current production focus is:

* Backend API versioning
* Stable `/api/v1` routes
* Single-club support for v1
* Clean upgrade path for v2
* Clerk-based authentication
* Passing tests before every merge

Please keep contributions focused, tested, and easy to review.

---

## Project Structure

```text
ClubIQ/
├── Backend/      # Flask API
├── Frontend/     # Next.js frontend
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Development Rules

Before contributing, follow these rules:

1. Do not rewrite working code without a clear reason.
2. Do not mix unrelated changes in one pull request.
3. Keep backend and frontend changes separate where possible.
4. Make small, reviewable commits.
5. Run tests before pushing.
6. Do not commit secrets, API keys, `.env` files, or local machine configs.
7. Do not remove v1 behavior while building v2.
8. Keep v1 production-safe and backward-compatible unless a breaking change is approved.

---

## Branch Naming

Use clear branch names.

```text
backend-v1-versioning
backend-auth-fix
backend-members-cleanup
frontend-dashboard-update
docs-readme-update
```

Preferred format:

```text
area/short-description
```

Examples:

```text
backend/add-v1-members-route
frontend/fix-admin-sidebar
docs/update-api-docs
tests/add-activity-tests
```

---

## Backend Setup

From the project root (requires Python 3.13; see `Backend/.python-version`):

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest -v
```

All backend tests must pass before opening a pull request.

---

## Frontend Setup

From the project root:

```bash
cd Frontend
npm install
npm run dev
```

Build check:

```bash
npm run build
```

---

## Docker Setup

From the project root:

```bash
cp Backend/backend.env.example Backend/backend.env
cp Frontend/frontend.env.example Frontend/frontend.env
cp Backend/postgres.env.example Backend/postgres.env
```

After setting up the environment variables, run the following command to start the services:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs backend -f
```

View frontend logs:

```bash
docker compose logs frontend -f
```

---

## Backend Contribution Guidelines

The backend uses Flask with separated modules.

Current backend structure:

```text
Backend/app/
├── auth/
├── members/
├── clubs/
├── activities/
├── invitations/
├── rating/
├── health/
├── api/
└── models.py
```

Follow the existing separation:

```text
routes.py      -> route/resource registration
resources.py   -> HTTP request/response handling
service.py     -> business logic
models.py      -> database models
```

Do not put business logic directly in route registration files.

---

## API Versioning Rules

The current production target is `/api/v1`.

v1 must stay simple:

```text
/api/v1/health
/api/v1/auth
/api/v1/members
```

Additional v1 routes (e.g. `clubs`, `activities`, `ratings`) should be added incrementally as they are implemented and mounted under the v1 blueprint.
Do not expose multi-club behavior in v1 unless approved.

Do not expose local invitation routes in v1. Clerk handles authentication and invitations.

v2 should be added later without breaking v1.

Do not copy the whole backend into `v1`, `v2`, or `v3` folders. Versioning should happen through a small API version layer, while shared business logic remains reusable.

---

## Backend Testing

Before pushing backend changes, run:

```bash
cd Backend
source .venv/bin/activate
pytest -v
```

Expected result:

```text
all tests passed
```

If tests fail, fix them before opening a pull request.

When adding or changing behavior, add or update tests.

---

## Database and Migrations

If your change modifies models, create a migration.

Do not manually edit the production database.

Do not delete existing columns or tables unless the migration plan is approved.

For v1, avoid destructive database changes. v1 data must remain compatible with future v2 multi-club support.

---

## Authentication Rules

ClubIQ uses Clerk for authentication.

Do not add a separate password system.

Do not build a custom invitation system for v1.

Do not store raw tokens or secrets in the database.

Backend responsibilities:

```text
verify Clerk identity
sync local user/member data
enforce roles and permissions
protect club data
```

Clerk responsibilities:

```text
sign up
sign in
email verification
session management
invitations
```

---

## Pull Request Checklist

Before opening a pull request, confirm:

* [ ] The branch name is clear.
* [ ] The change is focused.
* [ ] Backend tests pass.
* [ ] Frontend builds if frontend was changed.
* [ ] No secrets are committed.
* [ ] No unrelated formatting changes are included.
* [ ] API changes are documented.
* [ ] v1 behavior is not broken.
* [ ] Existing tests were not removed to hide failures.

---

## Commit Message Style

Use clear commit messages.

Good examples:

```text
Add v1 health API route
Add v1 auth API routes
Fix member role update permissions
Update backend API documentation
Add tests for activity creation
```

Bad examples:

```text
fix
changes
update stuff
work
final
```

---

## Code Review Expectations

Pull requests should be easy to review.

A good pull request explains:

```text
what changed
why it changed
how it was tested
any risks or follow-up work
```

If the change affects the backend API, include example routes or responses.

If the change affects authentication, permissions, database models, or production behavior, explain the impact clearly.

---

## Documentation

Update documentation when changing:

```text
API routes
request bodies
response bodies
environment variables
Docker commands
setup steps
deployment behavior
```

Backend endpoint documentation lives in:

```text
Backend/endpoint_documentation/
```

---

## Security

Do not commit:

```text
.env
API keys
database passwords
Clerk secrets
JWT secrets
private keys
production credentials
```

If a secret is committed by mistake, report it immediately and rotate the secret.

---

## Reporting Issues

When reporting a bug, include:

```text
what you expected
what happened
steps to reproduce
logs or error output
environment details
```

For backend bugs, include:

```text
route called
request body
response body
pytest output if available
```

---

## Production Focus

ClubIQ is not treated as a hobby project.

Contributions should keep the system:

```text
stable
testable
secure
easy to deploy
easy to upgrade from v1 to v2
```

When unsure, choose the smaller and safer change.
