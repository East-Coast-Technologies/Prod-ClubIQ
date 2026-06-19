# **Club IQ**

<p align='center'>
<img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python">
<img src="https://img.shields.io/badge/Flask-Backend-black?logo=flask">
<img src="https://img.shields.io/badge/Next.js-Frontend-black?logo=nextdotjs">
<img src="https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql">
<img src="https://img.shields.io/badge/Docker-Containerized-blue?logo=docker">
<img src="https://img.shields.io/badge/Clerk-Authentication-4F46E5?logo=clerk">
<img src="https://img.shields.io/badge/License-MIT-green">
<img src="https://img.shields.io/badge/Maintained-Yes-brightgreen.svg">
<img src="https://img.shields.io/github/contributors/tomi3-11/ClubIQ">
<a href="https://github.com/tomi3-11/ClubIQ/actions/workflows/ci.yaml">
<img src="https://github.com/tomi3-11/ClubIQ/actions/workflows/ci.yaml/badge.svg" alt="Club IQ CI">
</a>
</p>

---

# **Overview**

**Club IQ** is a full-stack platform for managing clubs: members, events, attendance, authentication, and more.

It includes:

* **Flask REST API**
* **Next.js frontend**
* **PostgreSQL** relational DB
* Full **Docker** environment
* **Clerk** authentication
* **Scalable architecture** for real-world clubs and organizations

---

# **Table of Contents**

<!--toc:start-->
- [**Club IQ**](#club-iq)
- [**Overview**](#overview)
- [**Table of Contents**](#table-of-contents)
- [**Project Structure**](#project-structure)
- [**Setup & Installation**](#setup-installation)
- [**Step 1 — Install Docker**](#step-1-install-docker)
- [**Step 2 — (Recommended) Setup Node in WSL using NVM**](#step-2-recommended-setup-node-in-wsl-using-nvm)
    - [Install NVM](#install-nvm)
    - [Install Node (LTS)](#install-node-lts)
    - [Verify WSL paths](#verify-wsl-paths)
- [**Step 3 — Install Make**](#step-3-install-make)
- [**Step 4 — Creating the Containers**](#step-4-creating-the-containers)
    - [Build all services:](#build-all-services)
    - [Run containers (attached):](#run-containers-attached)
    - [Detached mode:](#detached-mode)
- [**Manual Setup**](#manual-setup)
- [**Frontend Setup (Next.js)**](#frontend-setup-nextjs)
- [**API Reference**](#api-reference)
    - [Base URLs](#base-urls)
    - [Endpoint Documentation. All blueprints for backend](#endpoint-documentation-all-blueprints-for-backend)
- [**License**](#license)
<!--toc:end-->

---

# **Project Structure**

```
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
├── .env.example
├── docker-compose.yml
├── Makefile
├── .dockerignore
└── Docker.md
```

---

# **Setup & Installation**

Works on **Windows**, and **Linux**.
Follow the steps as listed — skipping ahead is how people summon bugs from the abyss.

---

# **Step 1 — Install Docker**
We recommend installing **Docker Desktop** as it not only installs Docker Desktop but also the **Docker Engine, Docker CLI, and Docker Compose.**

Download: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

During installation:

* Enable **Hyper-V / Virtualization**
* Enable **WSL2** backend

After installation, make sure the **Docker Daemon / docker.service** is running in the background otherwise **none** of the make or docker commands will work.

**Note: Using Docker Desktop / Podman Desktop is completely optional but is recommended since it makes it easy to manage your containers.**

---

# **Step 2 — (Recommended) Setup Node in WSL using NVM**

On Windows, use **WSL** for Node development or you’ll meet npm’s mood swings.

### Install NVM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
```

### Install Node (LTS)

```bash
nvm install --lts
nvm use --lts
```

### Verify WSL paths

```bash
which node
which npm
node -v
npm -v
```

Paths must **not** point to Windows directories.

---

# **Step 3 — Install Make**

`gnu make` is optional but we highly recommend installing it.

Install it by either visiting the [official Make website](https://www.gnu.org/software/make/) or using your package manager.

---

# **Step 4 — Creating the Containers**

View the our [**Docker.md**](./Docker.md) file for the full installation steps.
### Build all services:

```bash
make build
```

### Run containers (attached):

```bash
make up
```

### Detached mode:

```bash
make up-detached
```

---

# **Manual Setup**

If you want to setup the project without using Docker:

```bash
cd Backend

python -m venv venv

# Activate:
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

pip install -r requirements.txt

flask run
```

Environment variables are read from the process environment.

For Docker workflows, use `Backend/backend.env` and `Frontend/frontend.env` (see [Docker Guide](./Docker.md)).

---

# **Frontend Setup (Next.js)**

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs on:

[http://localhost:3000](http://localhost:3000)

---

# **API Reference**

### Base URLs

* Dev: `http://localhost:5000/api`
* Prod: `https://yourdomain.com/api`

---

### Endpoint Documentation. All blueprints for backend

- [V1](./Backend/endpoint_documentation/v1.md)
- [Authentication](./Backend/endpoint_documentation/authentication.md)
- [Clubs](./Backend/endpoint_documentation/clubs.md)
- [Members](./Backend/endpoint_documentation/members.md)
- [Activities](./Backend/endpoint_documentation/activities.md)
- [Rating](./Backend/endpoint_documentation/ratings.md)
- [Invitation](./Backend/endpoint_documentation/invitations.md)
- [Health](./Backend/endpoint_documentation/health.md)

---

# **License**

[MIT License.](./LICENSE)
