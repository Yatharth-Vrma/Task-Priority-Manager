# Claude AI Guidance for Task Manager Project

## Purpose

This document defines rules and constraints for AI-assisted development to maintain system integrity, correctness, and quality. Every rule exists because violating it would cause a specific, observable failure.

---

## Core Principles

1. **Correctness Over Features** — Every feature must be provably correct via tests
2. **Simplicity Over Cleverness** — Readable code beats clever code
3. **Explicit Over Implicit** — Make assumptions visible in code
4. **Fail Fast** — Invalid states should be impossible, not handled after the fact

---

## Architecture Rules

### Layered Architecture — Dependency Flow

```
Routes (app/routes/tasks.py)
  → Schemas (app/schemas/task.py)        # validation boundary
    → Services (app/services/task_service.py)  # business logic
      → Models (app/models/task.py)        # domain + DB schema
        → Database (app/database/__init__.py)
```

**NEVER** reverse dependencies:
- Models must NOT import from services
- Services must NOT import from routes
- Schemas must NOT import from services

### Adding a New Feature — Checklist

| Step | File(s) to touch | What to do |
|------|------------------|------------|
| 1 | `app/models/task.py` | Add column / enum value |
| 2 | `app/schemas/task.py` | Add field to `TaskCreate`, `TaskUpdate`, `TaskResponse` |
| 3 | `app/services/task_service.py` | Add/update business logic methods |
| 4 | `app/routes/tasks.py` | Wire new service call (only if new endpoint) |
| 5 | `tests/test_task_service.py` | Unit tests for new service logic |
| 6 | `tests/test_api.py` | Integration tests for new endpoint behaviour |
| 7 | `frontend/src/types/Task.ts` | Mirror the schema change |
| 8 | Component files | Update UI |

### Adding a New Status Value

1. Add value to `Status` enum in `app/models/task.py`
2. Update `can_transition()` valid_transitions dict in same file
3. Update `_get_valid_transitions()` in `app/services/task_service.py`
4. Add to `Status` enum in `frontend/src/types/Task.ts`
5. Update `TaskItem.tsx` action buttons
6. Write tests for every new transition edge

### Adding a New Priority Value

1. Add value to `Priority` enum in `app/models/task.py`
2. Add to `Priority` enum in `frontend/src/types/Task.ts`
3. Add `<option>` in `TaskForm.tsx` and `FilterBar.tsx`
4. Add CSS class in `App.css` for the new priority colour
5. That's it — schemas and routes need zero changes

---

## Code Generation Rules

### Python Backend

**MUST**:
- Use type hints on every function signature
- Use Pydantic schemas with `extra='forbid'` for all input validation
- Write docstrings for every public method
- Raise specific exceptions (`TaskNotFoundError`, `InvalidStatusTransitionError`)
- Guard `request.get_json()` — it can return `None`
- Use `logger.info()` / `logger.warning()` for observable state changes
- Follow PEP 8

**MUST NOT**:
- Use bare `except Exception` without a specific fallback
- Access `db.session` from routes — only through services
- Use `datetime.utcnow()` — use `datetime.now(timezone.utc)` via `_utcnow()`
- Return `None` when data is expected — raise instead
- Use raw SQL strings — use SQLAlchemy ORM
- Catch and silently swallow errors

**Example — Correct**:
```python
@tasks_bp.route('', methods=['POST'])
def create_task():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(ErrorResponse(error="Request body must be valid JSON").model_dump()), 400
    data = TaskCreate(**body)
    task = TaskService.create_task(data)
    return jsonify(TaskResponse.model_validate(task).model_dump()), 201
```

**Example — Wrong**:
```python
@tasks_bp.route('', methods=['POST'])
def create_task():
    data = TaskCreate(**request.get_json())  # crashes on None body
    # ...
```

### React / TypeScript Frontend

**MUST**:
- Use TypeScript for all files
- Define explicit interfaces for all component props
- Handle loading and error states in every component that calls the API
- Use `useCallback` for functions passed as deps or to children
- Use `task.id` as React key (never index)

**MUST NOT**:
- Use `any` type — use `unknown` or a specific interface
- Mutate state directly — always use setter from `useState`
- Use `@ts-ignore` or `@ts-expect-error`
- Use inline styles for anything that should be a reusable class

---

## State Machine Rules

The task status state machine is the single most important business rule.

```
PENDING ──→ IN_PROGRESS ──→ COMPLETED (terminal)
              │
              └──→ PENDING (rollback)
```

- `COMPLETED` is **terminal** — no transitions out
- `PENDING → COMPLETED` is **forbidden** — must go through `IN_PROGRESS`
- Enforcement lives in `Task.can_transition()` (model) and `TaskService.update_task_status()` (service)
- Two duplicate transition maps exist intentionally: `can_transition()` for the check, `_get_valid_transitions()` for error messages

---

## Testing Requirements

### What Must Be Tested

| Behaviour | Test file | Why |
|-----------|-----------|-----|
| Every valid status transition | `test_task_service.py` | Core business rule |
| Every invalid status transition | `test_task_service.py` | Proves bad states are impossible |
| Malformed/missing JSON body | `test_api.py::TestEdgeCases` | Prevents 500 errors in production |
| Extra fields rejected | `test_api.py::TestEdgeCases` | Proves schema strictness |
| Boundary lengths (title 200, desc 1000) | `test_api.py::TestEdgeCases` | Proves validation works at edges |
| Complete CRUD lifecycle | `test_api.py::test_complete_workflow` | End-to-end sanity check |

### Running Tests

```bash
cd backend && source venv/bin/activate
pytest tests/ -v            # all tests, verbose
pytest tests/ -v --tb=short # short tracebacks on failure
```

**Expected**: 56 passed, 0 warnings

---

## Validation Strategy (Defence in Depth)

1. **Pydantic schemas** — type + length + format validation at API boundary
2. **Service layer** — business rule validation (state transitions)
3. **SQLAlchemy model** — `CheckConstraint("length(trim(title)) > 0")` as last-resort DB guard
4. **Frontend** — client-side validation for UX (not trusted for correctness)

---

## Error Handling Strategy

```
Domain exceptions (services)  →  HTTP status codes (routes)
  TaskNotFoundError           →  404
  InvalidStatusTransitionError →  400
  ValidationError (Pydantic)  →  400
  Exception (unexpected)      →  400 (with message)
```

All error responses use the `ErrorResponse` schema: `{ "error": "...", "details": [...] }`

---

## Observability

- **Request logging**: `before_request` / `after_request` hooks in `app/__init__.py` log method, path, status code
- **Service logging**: `logger.info()` on create, update, delete; `logger.warning()` on not-found
- **Health check**: `GET /health` returns `{"status": "healthy"}` — excluded from request logs to avoid noise

---

## Common Mistakes to Avoid

| Mistake | Why it's bad | Fix |
|---------|-------------|-----|
| `request.get_json()` without `None` check | Crashes with `TypeError` on empty body | Use `silent=True` + guard |
| `datetime.utcnow()` | Deprecated in Python 3.12+, returns naive datetime | Use `_utcnow()` helper |
| `class Config:` in Pydantic v2 | Deprecated, emits warning | Use `model_config = ConfigDict(...)` |
| `any` in TypeScript | Breaks type safety, hides bugs | Use `unknown` or specific type |
| Catching generic `Exception` silently | Hides real bugs | Re-raise or log + specific catch |
| Duplicate transition maps | Can drift apart | Document why both exist; they serve different purposes |

---

## AI-Specific Rules

When generating code for this project:

1. **Always include type hints** — no exceptions
2. **Always validate inputs** — trust nothing from the client
3. **Always handle errors explicitly** — no silent failures
4. **Always write tests for new behaviour** — not optional
5. **Always document _why_, not _what_** — the code shows what

---

## Review Checklist

Before accepting any AI-generated change:

- [ ] All functions have type hints
- [ ] All inputs validated through Pydantic schemas with `extra='forbid'`
- [ ] `request.get_json(silent=True)` guarded against `None`
- [ ] New service methods have `logger.info()`/`logger.warning()` calls
- [ ] Tests cover happy path AND error path
- [ ] No `any` types in TypeScript
- [ ] No `datetime.utcnow()` — use `_utcnow()` helper
- [ ] No `class Config:` — use `model_config = ConfigDict(...)`
- [ ] Dependencies flow downward only (routes → services → models)
- [ ] Frontend error/loading states handled
