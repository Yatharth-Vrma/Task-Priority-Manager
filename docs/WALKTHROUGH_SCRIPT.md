# Video Walkthrough Script

**Duration: 10-15 minutes**

---

## Introduction (1 minute)

"Hello! I'm Yatharth, and this is my submission for the Associate Software Engineer assessment at Better Software.

I've built a Task Priority Manager - a simple but well-engineered task management system that demonstrates clean architecture, type safety, and correctness-first design.

Let me walk you through the architecture, technical decisions, how I used AI, and potential risks and extensions."

---

## System Overview (2 minutes)

"The system consists of:
- A Flask REST API backend with Python
- A React frontend with TypeScript
- SQLite database
- Comprehensive automated tests

The key principle I followed was: **Correctness over features**. Every design decision prioritizes preventing invalid states and maintaining system integrity as it evolves."

[Show project structure on screen]

```
task-manager/
├── backend/          # Flask API
│   ├── app/
│   │   ├── models/   # Domain models
│   │   ├── schemas/  # Pydantic validation
│   │   ├── services/ # Business logic
│   │   └── routes/   # API endpoints
│   └── tests/        # Automated tests
├── frontend/         # React app
│   └── src/
│       ├── components/
│       ├── services/
│       └── types/
└── docs/            # Documentation
```

---

## Architecture Deep Dive (4 minutes)

### Backend Layers

"The backend follows strict layered architecture:

**1. Routes Layer** - HTTP only
- Parses requests
- Delegates to services
- Returns responses
- No business logic

**2. Schemas Layer** - Validation boundary
- Pydantic models ensure type safety
- Runtime validation catches bad data
- Nothing gets past this layer without validation

**3. Services Layer** - Business logic
- Where the real work happens
- Enforces business rules
- No HTTP concerns

**4. Models Layer** - Domain and persistence
- Database schema
- Domain constraints
- State transition rules"

[Show code example of each layer]

### Key Design Pattern: State Machine

"Tasks have three states: PENDING → IN_PROGRESS → COMPLETED

Invalid transitions are impossible by design, not caught by error handling."

[Show `Task.can_transition()` method]

```python
@staticmethod
def can_transition(from_status: Status, to_status: Status) -> bool:
    valid_transitions = {
        Status.PENDING: {Status.IN_PROGRESS},
        Status.IN_PROGRESS: {Status.COMPLETED, Status.PENDING},
        Status.COMPLETED: set()  # Terminal state
    }
    return to_status in valid_transitions.get(from_status, set())
```

"Notice: COMPLETED is a terminal state. Once done, a task can't be undone. This prevents data corruption."

### Frontend Architecture

"React frontend mirrors backend structure:
- TypeScript types match backend schemas exactly
- API service layer centralizes HTTP calls
- Component composition keeps UI simple
- State flows down, events flow up"

[Show type definitions and API service]

---

## Technical Decisions (3 minutes)

### Why Layered Architecture?

"Three main benefits:

1. **Change Resilience**: Adding a new field only requires updating the model and schema. Routes and services continue working.

2. **Testability**: Each layer can be tested in isolation. No need to spin up HTTP server to test business logic.

3. **Clarity**: Each file has one job. When debugging, you know exactly where to look."

### Why Pydantic?

"Runtime validation is crucial. Without it, invalid data could reach the database.

Example: Empty task titles"

[Show schema validation]

```python
class TaskCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str = Field(..., min_length=1, max_length=200)
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

"Notice `extra='forbid'` — any unknown fields in the request body are rejected immediately. This prevents silent data loss."

### Why SQLAlchemy?

"Three reasons:
1. **SQL Injection Prevention**: Parameterized queries by default
2. **Type Safety**: Python objects, not string queries
3. **Database Agnostic**: Easy migration from SQLite to PostgreSQL"

### What I Deliberately Left Out

"I focused on demonstrating core engineering skills, not feature count:

- **No Authentication**: Adds complexity without showing architecture skills
- **No Real-time Updates**: WebSockets would obscure the clean REST design
- **No Pagination**: Can be added easily later (demonstrates change resilience)

Each omission was intentional to keep the codebase clear and focused."

---

## AI Usage (2 minutes)

### How I Used Claude

"I used Claude extensively, but with strict constraints. Here's my approach:

**1. Created AI Guidance Document** (`docs/claude-guidance.md`)
- Defines coding standards
- Mandates type hints everywhere
- Requires explicit error handling
- Prevents common AI mistakes like using `any` types

**2. Iterative Code Generation**
- Generated boilerplate (models, schemas, routes)
- Reviewed every line
- Refactored for clarity
- Added tests to verify behavior

**3. Documentation**
- Used AI to draft documentation
- Rewrote for accuracy and clarity
- Ensured it matched actual implementation"

### What I Verified

"Every AI-generated piece was verified:
- Type hints are correct
- Error handling is explicit
- Tests actually pass
- Logic matches requirements

AI accelerated development, but I remained the critical reviewer."

---

## Testing & Verification (2 minutes)

### Test Coverage

"I have **56 automated tests** across three categories:

**22 Integration Tests** - Full HTTP round-trips for every endpoint
**17 Edge-Case Tests** - Malformed JSON, boundary lengths, extra fields rejected, invalid filters, terminal state enforcement
**17 Unit Tests** - Business logic in isolation"

[Show test example]

```python
def test_invalid_status_transition_pending_to_completed(self, db):
    task = TaskService.create_task(TaskCreate(title="Test"))
    
    with pytest.raises(InvalidStatusTransitionError):
        TaskService.update_task_status(task.id, Status.COMPLETED)
```

"This proves the state machine works correctly."

**Integration Tests** - API endpoints end-to-end"

[Show test example]

```python
def test_complete_workflow(self, client):
    # Create task
    create_resp = client.post('/api/tasks', json={...})
    task_id = create_resp.json['id']
    
    # Start working
    client.put(f'/api/tasks/{task_id}/status', 
               json={'status': 'IN_PROGRESS'})
    
    # Complete
    client.put(f'/api/tasks/{task_id}/status',
               json={'status': 'COMPLETED'})
```

"This tests the entire stack."

[Run tests and show results]

```bash
pytest tests/ -v
# 56 passed, 0 warnings
```

---

## Risks & Mitigation (1 minute)

### Current Risks

"1. **No Authentication**: Anyone can access the API
   - Mitigation: Add JWT tokens before production

2. **SQLite Limitations**: Not suitable for high concurrency
   - Mitigation: Migrate to PostgreSQL (already designed for this)

3. **No Rate Limiting**: API can be abused
   - Mitigation: Add Flask-Limiter

4. **In-Memory Database**: Data resets on restart
   - Mitigation: Use file-based SQLite or PostgreSQL"

---

## Extension Approach (1-2 minutes)

### How to Add Features Without Breaking Things

"Example: Adding due dates

**Step 1**: Add column to model
```python
due_date = db.Column(db.DateTime, nullable=True)
```

**Step 2**: Update schema
```python
class TaskCreate(BaseModel):
    due_date: Optional[datetime] = None
```

**Step 3**: That's it!

Existing code continues working. Validation is automatic. Tests still pass.

This is **change resilience** in action."

### More Complex Extensions

"**Sub-tasks** (hierarchical tasks):
- Add `parent_id` foreign key
- Add validation to prevent circular dependencies
- Service methods compose existing patterns
- No changes to routes needed

**Tags/Categories**:
- New table with many-to-many relationship
- New schema for tag operations
- New service methods
- Routes follow existing CRUD patterns

**Audit Log**:
- SQLAlchemy event listeners
- Log all changes to separate table
- Zero changes to existing code

The architecture naturally supports these extensions."

---

## Conclusion (1 minute)

"To summarize:

**What I built**: A task manager that prioritizes correctness and simplicity

**Key strengths**:
- Layered architecture prevents coupling
- Type safety from end to end
- Invalid states are impossible
- Changes are localized
- 56 automated tests verify every edge

**AI usage**: Strategic and verified
- Used for boilerplate and acceleration
- All code reviewed and tested
- Clear guidance documents prevented common mistakes

**Trade-offs**: Deliberately simple to demonstrate principles clearly

This system is small, but it's built to grow correctly.

Thank you for your time. I'm happy to answer any questions."

---

## Demo (If time allows - 1 minute)

[Show the application running]

1. Create a task
2. Start working on it (PENDING → IN_PROGRESS)
3. Try to complete directly from PENDING (fails with clear error)
4. Complete from IN_PROGRESS (succeeds)
5. Show filtered views
6. Delete a task

"Notice how the state transitions are enforced by the backend, and the UI reflects this with disabled buttons."
