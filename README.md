# Task Priority Manager

A task management system demonstrating clean architecture, type safety, and correctness-first design.

> **Yatharth Verma** · Associate Software Engineer Assessment · Better Software

---

## 📹 Video Walkthrough

<!-- 
  OPTION 1: Local video in repo (recommended for GitHub)
  Place your video at video/walkthrough.mp4 and uncomment:
-->
<!--
<video src="video/walkthrough.mp4" controls width="100%">
  Your browser does not support the video tag.
</video>
-->

<!-- 
  OPTION 2: YouTube / Loom link
  Replace YOUR_VIDEO_ID with your actual video ID:
-->
<!-- [![Watch the Walkthrough](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID) -->

> **⬆️ After recording, uncomment one of the options above and delete the other.**
>
> The walkthrough covers: Architecture · Code structure · Technical decisions · AI usage · Risks · Extension approach
>
> Script: [`docs/WALKTHROUGH_SCRIPT.md`](docs/WALKTHROUGH_SCRIPT.md)

---

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Key Technical Decisions](#-key-technical-decisions)
- [Core Features](#-core-features)
- [API Reference](#-api-reference)
- [Verification Strategy](#-verification-strategy)
- [Observability](#-observability)
- [Risks & Mitigation](#-risks--mitigation)
- [Change Resilience & Extension Approach](#-change-resilience--extension-approach)
- [Known Limitations](#-known-limitations)
- [AI Usage](#-ai-usage)
- [AI Guidance Files](#-ai-guidance-files)
- [Project Structure](#-project-structure)
- [Documentation Index](#-documentation-index)

---

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py              # → http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm start                  # → http://localhost:3000
```

### Run Tests

```bash
cd backend && source venv/bin/activate
pytest tests/ -v
# Expected: 56 passed, 0 warnings
```

For detailed setup (troubleshooting, env vars, production deployment): [`docs/SETUP.md`](docs/SETUP.md)

---

## 🏗 Architecture

```
┌─────────────────────────────────┐
│   Frontend (React + TypeScript) │
│   Components → API Service      │
└───────────────┬─────────────────┘
                │ HTTP / JSON
┌───────────────▼─────────────────┐
│   Backend (Flask + Python)      │
│                                 │
│   Routes ─→ Schemas (Pydantic)  │
│     │                           │
│   Services (business logic)     │
│     │                           │
│   Models (SQLAlchemy ORM)       │
│     │                           │
│   SQLite Database               │
└─────────────────────────────────┘
```

Each layer has **one responsibility**. Dependencies flow **downward only** — routes never import from models, services never know about HTTP.

| Layer | Responsibility | Key File |
|-------|---------------|----------|
| **Routes** | Parse HTTP, serialize responses, map errors → status codes | [`app/routes/tasks.py`](backend/app/routes/tasks.py) |
| **Schemas** | Validate input/output with Pydantic (`extra='forbid'`) | [`app/schemas/task.py`](backend/app/schemas/task.py) |
| **Services** | Business logic, state machine enforcement, logging | [`app/services/task_service.py`](backend/app/services/task_service.py) |
| **Models** | Domain entities, DB schema, constraints, transition rules | [`app/models/task.py`](backend/app/models/task.py) |
| **Database** | SQLAlchemy ORM initialisation | [`app/database/__init__.py`](backend/app/database/__init__.py) |

Full architecture deep-dive: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 🔑 Key Technical Decisions

### Why Layered Architecture?
**Benefit**: each layer can change independently. Adding a CLI or background worker reuses the service layer — zero route changes.  
**Trade-off**: extra indirection for a small app. Pays for itself the moment a second consumer appears.

### Why Pydantic with `extra='forbid'`?
**Benefit**: runtime validation catches invalid data *before* it reaches the database; rejecting unknown fields prevents silent data loss or accidental field injection.  
**Trade-off**: slightly more verbose schema definitions. Worth it for the safety guarantee.

### Why SQLite?
**Benefit**: zero configuration, file-based, sufficient for assessment scope.  
**Trade-off**: single-writer, not suitable for concurrent production load. Swap to PostgreSQL by changing one config line — the ORM abstracts the difference.

### Why a Service Layer?
**Benefit**: business logic separated from HTTP. Services can be reused from CLI tools, background jobs, tests, or any future entry point.  
**Trade-off**: one more file to read. Clear naming makes this trivial.

### Why No Authentication?
**Chosen because**: out of scope. Adding auth would demonstrate JWT knowledge but obscure the architecture patterns being evaluated. Adding it later requires a `User` model + middleware — minimal changes to existing code.

### Why No Pagination?
**Chosen because**: not needed at current scale. Adding it later:
1. Add `page`/`per_page` to `TaskService.get_all_tasks()`
2. Accept query params in route
3. No schema changes

This is a concrete example of **change resilience**.

---

## ✨ Core Features

### Task CRUD
- Create tasks with title (1–200 chars), optional description (max 1000 chars), priority
- Partial updates — only send the fields you want to change
- Delete tasks permanently
- List all tasks with optional status/priority filtering

### Priority System
Three levels: `LOW` · `MEDIUM` · `HIGH`. Default: `MEDIUM`.  
Validated at schema level — invalid values are rejected before reaching business logic.

### Status State Machine

```
PENDING ──→ IN_PROGRESS ──→ COMPLETED (terminal)
                │
                └──→ PENDING (rollback)
```

- Tasks always start as `PENDING`
- Cannot skip `PENDING → COMPLETED` — must go through `IN_PROGRESS`
- `COMPLETED` is **terminal** — no transitions out
- `IN_PROGRESS → PENDING` rollback is intentionally allowed
- Enforcement: [`Task.can_transition()`](backend/app/models/task.py) + [`TaskService.update_task_status()`](backend/app/services/task_service.py)

---

## 📡 API Reference

| Method | Path | Description | Codes |
|--------|------|-------------|-------|
| `GET` | `/api/tasks` | List tasks (`?status=` / `?priority=` filters) | 200, 400 |
| `GET` | `/api/tasks/:id` | Get task by ID | 200, 404 |
| `POST` | `/api/tasks` | Create task | 201, 400 |
| `PUT` | `/api/tasks/:id` | Update task details | 200, 400, 404 |
| `PUT` | `/api/tasks/:id/status` | Update task status | 200, 400, 404 |
| `DELETE` | `/api/tasks/:id` | Delete task | 204, 404 |
| `GET` | `/health` | Health check | 200 |

<details>
<summary><strong>Example: Full Task Lifecycle</strong></summary>

```bash
# 1. Create
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Review PR", "priority": "HIGH"}'

# 2. Start working
curl -X PUT http://localhost:5000/api/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}'

# 3. Complete
curl -X PUT http://localhost:5000/api/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "COMPLETED"}'

# 4. Filter
curl http://localhost:5000/api/tasks?status=COMPLETED
```

</details>

---

## ✅ Verification Strategy

### Defence in Depth

Invalid data is blocked at **four levels**:

| Level | What it catches | Where |
|-------|----------------|-------|
| **Frontend** | Missing title, UX feedback | `TaskForm.tsx` |
| **Pydantic schemas** | Type, length, format, extra fields | `app/schemas/task.py` |
| **Service layer** | Invalid state transitions, not-found | `app/services/task_service.py` |
| **Database constraints** | `CHECK(length(trim(title)) > 0)`, `NOT NULL` | `app/models/task.py` |

### Test Suite

| Category | Count | What it covers |
|----------|-------|---------------|
| Integration tests (`TestTaskAPI`) | 22 | Full HTTP round-trips for every endpoint |
| Edge-case tests (`TestEdgeCases`) | 17 | Malformed JSON, boundary lengths, extra fields, invalid filters, terminal state |
| Unit tests (`TestTaskService`) | 17 | Business logic in isolation — every transition edge |
| **Total** | **56** | **0 warnings** |

```bash
pytest tests/ -v
# 56 passed, 0 warnings
```

---

## 👁 Observability

| Signal | Implementation | File |
|--------|---------------|------|
| **Request/response logging** | `before_request` / `after_request` hooks — method, path, status code (health excluded) | [`app/__init__.py`](backend/app/__init__.py) |
| **Service logging** | `logger.info()` on create/update/delete; `logger.warning()` on not-found | [`app/services/task_service.py`](backend/app/services/task_service.py) |
| **Structured errors** | Consistent `{"error": "...", "details": [...]}` format across all 400/404 responses | [`app/schemas/task.py`](backend/app/schemas/task.py) |
| **Health endpoint** | `GET /health` → `{"status": "healthy"}` | [`app/__init__.py`](backend/app/__init__.py) |

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Mitigation Path |
|------|--------|-----------------|
| **No authentication** | Anyone can CRUD any task | Add JWT middleware + `User` model; service layer unchanged |
| **SQLite concurrency** | Single-writer blocks under load | Swap `DATABASE_URL` to PostgreSQL; ORM abstracts the difference |
| **No rate limiting** | API can be abused | Add `Flask-Limiter` — 1 line decorator per route |
| **No pagination** | Slow with thousands of tasks | Add `page`/`per_page` to service + route; schema unchanged |
| **Hard deletes** | Data loss is permanent | Add `deleted_at` column for soft delete; filter in queries |

---

## 🔄 Change Resilience & Extension Approach

The architecture is designed so most changes touch **1–2 files**, not the whole stack.

<details>
<summary><strong>Adding a <code>due_date</code> field</strong></summary>

1. Add column to `Task` model
2. Add field to `TaskCreate`, `TaskUpdate`, `TaskResponse` schemas
3. **Done** — routes and services handle it automatically

</details>

<details>
<summary><strong>Adding an <code>ARCHIVED</code> status</strong></summary>

1. Add to `Status` enum in model
2. Update `can_transition()` dict — 1 line
3. Update `_get_valid_transitions()` dict — 1 line
4. Add frontend enum value + button
5. Write 2–3 transition tests

</details>

<details>
<summary><strong>Adding a new entity (e.g., Tags)</strong></summary>

1. New model → new schema → new service → new route → register blueprint
2. Follows the exact same pattern as Tasks

</details>

<details>
<summary><strong>Adding sub-tasks</strong></summary>

1. Self-referential `parent_id` foreign key on `Task`
2. Validation to prevent circular references
3. Existing CRUD continues working unchanged

</details>

---

## 📋 Known Limitations

| Limitation | Why it's intentional | Migration path |
|------------|---------------------|----------------|
| No authentication | Scope focus on architecture | JWT middleware |
| SQLite only | Zero-config simplicity | Change 1 env var for PostgreSQL |
| No pagination | Fine for <1000 tasks | Add params to service + route |
| Hard deletes | Simpler to reason about | Add `deleted_at` soft-delete column |
| No caching | Every request hits DB | Add Redis layer in service |
| In-memory DB for tests | Isolation by design | N/A — working as intended |

---

## 🤖 AI Usage

This project was built with **Claude (Anthropic)** AI assistance. AI was used for:

| Area | How AI helped | How I verified |
|------|--------------|----------------|
| **Boilerplate generation** | Model, schema, route scaffolding | Reviewed every line for correctness |
| **Test case generation** | Edge cases (malformed JSON, boundary lengths) | Ran full suite — 56 passed |
| **Documentation** | README, architecture docs, walkthrough script | Rewrote for accuracy, verified against code |
| **Debugging** | Pydantic v2 + Python 3.13 compatibility | Confirmed fix with passing tests |
| **Best practices** | Logging, error handling patterns | Cross-referenced with Flask/Pydantic docs |

**Key principle**: AI accelerated development, but I was the critical reviewer. Every piece of generated code was tested, and many sections were rewritten for clarity and correctness.

---

## 📎 AI Guidance Files

AI-generated code was constrained by explicit guidance documents:

| File | Purpose |
|------|---------|
| [`docs/claude-guidance.md`](docs/claude-guidance.md) | **Primary AI constraints** — coding standards, architecture rules, state machine rules, common mistakes to avoid, review checklist, file-level checklists for adding features |

### Key Constraints Enforced

- ✅ Type hints on every function — no exceptions
- ✅ `extra='forbid'` on all Pydantic input schemas
- ✅ `request.get_json(silent=True)` guarded against `None` in every route
- ✅ No `any` types in TypeScript — use `unknown` or specific interfaces
- ✅ No `datetime.utcnow()` — use `datetime.now(timezone.utc)` helper
- ✅ Dependencies flow downward only (routes → services → models)
- ✅ Every service method logs its operation
- ✅ Tests cover happy path AND error path

---

## 📁 Project Structure

```
task-manager/
├── README.md                    ← You are here
├── video/                       # Walkthrough video
│   └── walkthrough.mp4          # (add your recording here)
│
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory, CORS, request logging
│   │   ├── database/            # SQLAlchemy setup
│   │   ├── models/task.py       # Task model, enums, state machine
│   │   ├── schemas/task.py      # Pydantic validation (extra='forbid')
│   │   ├── services/task_service.py  # Business logic + logging
│   │   └── routes/tasks.py      # REST endpoints + JSON body guards
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── test_api.py          # 22 integration + 17 edge-case tests
│   │   └── test_task_service.py # 17 unit tests
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main component, state management
│   │   ├── App.css              # Design tokens, responsive layout
│   │   ├── components/          # TaskForm, TaskList, TaskItem, FilterBar
│   │   ├── services/api.ts      # Typed HTTP client (no `any`)
│   │   └── types/Task.ts        # TypeScript enums & interfaces
│   └── package.json
│
└── docs/
    ├── ARCHITECTURE.md          # Detailed architecture deep-dive
    ├── claude-guidance.md       # AI development constraints & rules
    ├── SETUP.md                 # Setup, troubleshooting, deployment
    ├── WALKTHROUGH_SCRIPT.md    # 10–15 min video script
    └── SUBMISSION_CHECKLIST.md  # Self-assessment checklist
```

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| [`README.md`](README.md) | Project overview, decisions, API reference (this file) |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layered architecture deep-dive, data flow diagrams, design patterns |
| [`docs/claude-guidance.md`](docs/claude-guidance.md) | AI coding constraints, review checklist, common mistake prevention |
| [`docs/SETUP.md`](docs/SETUP.md) | Detailed setup, environment variables, troubleshooting, production deployment |
| [`docs/WALKTHROUGH_SCRIPT.md`](docs/WALKTHROUGH_SCRIPT.md) | 10–15 minute video walkthrough script |
| [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md) | Self-assessment against evaluation criteria |
| [`video/README.md`](video/README.md) | Instructions for adding the walkthrough video |
