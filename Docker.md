# 🐳 **ClubIQ Docker Guide**

<!--toc:start-->
- [🐳 **ClubIQ Docker Guide**](#🐳-clubiq-docker-guide)
  - [Overview](#overview)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Project Services](#2-project-services)
  - [3. Directory Layout](#3-directory-layout)
  - [4. Environment Setup](#4-environment-setup)
  - [5. Build & Run](#5-build-run)
  - [6. Manual Docker Commands](#6-manual-docker-commands)
  - [7. Possible Issues](#7-possible-issues)
<!--toc:end-->

## Overview

This document explains how to build and run the **ClubIQ** Club Management System locally using Docker.
It includes the **Flask backend**, **Next.js frontend**, and **PostgreSQL database**.

The setup automatically handles:

* Database initialization and migrations
* Hot reloading for both backend and frontend
* Persistent Postgres storage

---

## 1. Prerequisites

Before running the containers, ensure you have:

* **Docker** ≥ 20.x
* **Docker Compose** plugin ≥ v2.0
* **Make** (optional, for easier commands)

---

## 2. Project Services

| Service      | Description                                        | Port   |
| ------------ | -------------------------------------------------- | ------ |
| **frontend** | Next.js development server (Clerk auth integrated) | `3000` |
| **backend**  | Flask API (with SQLAlchemy + migrations)           | `5000` |
| **postgres**       | PostgreSQL 17 (persistent volume)                  | `5432` |

---

## 3. Directory Layout

```text
ClubIQ/
├── Backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── backend.env.example
│   └── app/
│       ├── models.py
│       └── ...
│
├── Frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── frontend.env.example
│   └── src/
│
├── docker-compose.yml
├── Makefile
├── .dockerignore
└── Docker.md
```

---

## 4. Environment Setup

Copy and configure the example environment files:

```bash
cp Backend/backend.env.example Backend/backend.env
cp Frontend/frontend.env.example Frontend/frontend.env
```

Then open the two env files and replace values as needed.

---

## 5. Build & Run

Run all containers with:

```bash
make build
```

This automatically:

* Builds all images
* Initializes and migrates the database
* Launches the Flask + Next.js servers

Visit your app at:

* **Frontend:** [http://localhost:3000](http://localhost:3000)
* **Backend API:** [http://localhost:5000](http://localhost:5000)

To view the full list of commands provided through the Make file, run:

```bash
make help
```

---

## 6. Manual Docker Commands

If you don’t have `make` installed:

```bash
docker compose up --build
docker compose down
docker compose exec backend flask db upgrade
```

---

## 7. Possible Issues

| Problem                                         | Fix                                                              |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| Containers build but backend crashes on startup | Check `Backend/backend.env` and ensure `DATABASE_URL` matches service name `postgres` |
| Frontend can't reach API                        | Confirm `NEXT_PUBLIC_API_URL=http://localhost:5000`              |
| Frontend marked unhealthy                       | Confirm `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is present in `Frontend/frontend.env` and loaded by Compose |
| Backend marked unhealthy                        | Confirm `curl -f http://localhost:5000/api/backend-health` succeeds inside backend container |
| Migrations not running                          | Run `make migrate` manually inside backend container             |
| Database persists unwanted data                 | Run `make down-volumes` to reset Postgres volume                |

---
