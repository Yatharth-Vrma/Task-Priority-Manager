# Architecture Documentation

## System Overview

Task Priority Manager follows a clean, layered architecture with clear separation of concerns.

```
┌─────────────────────────────────────────┐
│           Frontend (React)              │
│  ┌───────────────────────────────────┐  │
│  │  Components (UI)                  │  │
│  │  ├─ TaskForm                      │  │
│  │  ├─ TaskList                      │  │
│  │  ├─ TaskItem                      │  │
│  │  └─ FilterBar                     │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Services (API Client)            │  │
│  │  └─ taskApi                       │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Types (TypeScript Interfaces)    │  │
│  │  └─ Task, Status, Priority        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    │
                HTTP/JSON
                    │
┌─────────────────────────────────────────┐
│           Backend (Flask)               │
│  ┌───────────────────────────────────┐  │
│  │  Routes (HTTP Handlers)           │  │
│  │  └─ /api/tasks/*                  │  │
│  └───────────────────────────────────┘  │
│                 │                       │
│  ┌───────────────────────────────────┐  │
│  │  Schemas (Pydantic Validation)    │  │
│  │  └─ TaskCreate, TaskUpdate        │  │
│  └───────────────────────────────────┘  │
│                 │                       │
│  ┌───────────────────────────────────┐  │
│  │  Services (Business Logic)        │  │
│  │  └─ TaskService                   │  │
│  └───────────────────────────────────┘  │
│                 │                       │
│  ┌───────────────────────────────────┐  │
│  │  Models (Domain Objects)          │  │
│  │  └─ Task, Status, Priority        │  │
│  └───────────────────────────────────┘  │
│                 │                       │
│  ┌───────────────────────────────────┐  │
│  │  Database (SQLAlchemy ORM)        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    │
                SQLite DB
```

## Backend Architecture

### Layer Responsibilities

#### 1. Routes Layer (`app/routes/`)
- **Purpose**: HTTP request/response handling
- **Responsibilities**:
  - Parse HTTP requests
  - Validate request format (JSON structure)
  - Call appropriate service methods
  - Serialize responses
  - Map exceptions to HTTP status codes
- **Does NOT**:
  - Contain business logic
  - Access database directly
  - Perform data validation (delegates to schemas)

**Example**:
```python
@tasks_bp.route('', methods=['POST'])
def create_task():
    data = TaskCreate(**request.get_json())  # Schema validation
    task = TaskService.create_task(data)     # Business logic
    return jsonify(task.to_dict()), 201      # Serialization
```

#### 2. Schemas Layer (`app/schemas/`)
- **Purpose**: Input/output validation and type safety
- **Responsibilities**:
  - Define data contracts
  - Validate input data
  - Provide type hints
  - Sanitize inputs (strip whitespace, etc.)
- **Does NOT**:
  - Contain business rules
  - Access database
  - Perform complex logic

**Example**:
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    priority: Priority = Field(default=Priority.MEDIUM)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

#### 3. Services Layer (`app/services/`)
- **Purpose**: Business logic execution
- **Responsibilities**:
  - Implement business rules
  - Orchestrate database operations
  - Enforce state transitions
  - Handle domain exceptions
- **Does NOT**:
  - Know about HTTP
  - Format responses
  - Parse requests

**Example**:
```python
def update_task_status(task_id: int, new_status: Status) -> Task:
    task = get_task(task_id)
    
    if not Task.can_transition(task.status, new_status):
        raise InvalidStatusTransitionError(...)
    
    task.status = new_status
    db.session.commit()
    return task
```

#### 4. Models Layer (`app/models/`)
- **Purpose**: Domain objects and database schema
- **Responsibilities**:
  - Define database schema
  - Represent domain entities
  - Enforce database constraints
  - Define relationships
  - Provide domain methods (e.g., `can_transition`)
- **Does NOT**:
  - Contain business logic
  - Know about HTTP or validation

**Example**:
```python
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(Enum(Status), default=Status.PENDING)
    
    __table_args__ = (
        CheckConstraint('length(title) > 0'),
    )
```

### Data Flow

#### Creating a Task

```
1. Client sends POST /api/tasks
   ↓
2. Routes: Parse JSON → Validate with TaskCreate schema
   ↓
3. Services: Create Task object → Save to DB
   ↓
4. Models: Enforce constraints → Return Task
   ↓
5. Routes: Serialize Task → Return 201 with JSON
```

#### Updating Status

```
1. Client sends PUT /api/tasks/1/status
   ↓
2. Routes: Parse JSON → Validate with StatusUpdate schema
   ↓
3. Services: Get Task → Check transition validity → Update
   ↓
4. Models: Apply constraints → Save
   ↓
5. Routes: Serialize → Return 200 with updated Task
```

## Frontend Architecture

### Component Structure

```
App (State Container)
├── TaskForm (Create Tasks)
├── FilterBar (Filter Controls)
└── TaskList (Display Tasks)
    └── TaskItem (Individual Task)
        ├── Status Badge
        ├── Priority Badge
        └── Action Buttons
```

### State Management

- **App Component**: Holds global state (tasks, filters)
- **Local State**: Each component manages its own UI state (loading, errors)
- **Props**: Data flows down, events flow up

**Example**:
```typescript
// App owns state
const [tasks, setTasks] = useState<Task[]>([]);

// TaskForm receives callback
<TaskForm onSubmit={handleCreateTask} />

// TaskList receives data and callbacks
<TaskList 
  tasks={tasks}
  onStatusChange={handleStatusChange}
  onDelete={handleDelete}
/>
```

### API Service Layer

Centralizes all HTTP communication:

```typescript
export const taskApi = {
  getAllTasks: (filters?) => Promise<Task[]>
  getTask: (id) => Promise<Task>
  createTask: (data) => Promise<Task>
  updateTask: (id, data) => Promise<Task>
  updateTaskStatus: (id, status) => Promise<Task>
  deleteTask: (id) => Promise<void>
}
```

**Benefits**:
- Easy to mock for testing
- Single source of truth for API calls
- Consistent error handling
- Type-safe requests/responses

## Design Patterns

### 1. Layered Architecture
- Clear separation of concerns
- Each layer has single responsibility
- Dependencies flow downward only

### 2. Repository Pattern (Service Layer)
- Abstracts database operations
- Business logic separated from persistence
- Easy to swap database implementations

### 3. Data Transfer Objects (Schemas)
- Separate external API from internal representation
- Validation at system boundaries
- Type safety end-to-end

### 4. Factory Pattern (Flask App)
- `create_app()` function creates configured app
- Easy to create test instances
- Configuration injection

### 5. Error Handling Strategy
- Domain exceptions in services
- HTTP error handlers in routes
- Consistent error responses

## Extension Points

### Adding a New Entity

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create service in `app/services/`
4. Create routes in `app/routes/`
5. Register blueprint in `app/__init__.py`

### Adding a New Feature to Tasks

**Example: Due Dates**

1. Add column to Task model:
```python
due_date = db.Column(db.DateTime, nullable=True)
```

2. Update schemas:
```python
class TaskCreate(BaseModel):
    due_date: Optional[datetime] = None
```

3. Service automatically handles it (no changes needed)

4. Routes automatically validate it (no changes needed)

5. Update frontend types and components

## Security Considerations

### Current Implementation

- **Input Validation**: Pydantic schemas
- **SQL Injection**: SQLAlchemy ORM (parameterized queries)
- **CORS**: Configured for localhost only
- **Error Messages**: Generic errors to clients

### Production Additions Needed

- **Authentication**: JWT tokens or session management
- **Authorization**: Role-based access control
- **Rate Limiting**: Prevent abuse
- **HTTPS**: Encrypt traffic
- **Input Sanitization**: XSS prevention
- **Database Encryption**: Sensitive data protection

## Performance Considerations

### Current Optimizations

- **Database Indexes**: On foreign keys
- **Query Efficiency**: ORM uses efficient queries
- **Connection Pooling**: SQLAlchemy default behavior

### Future Optimizations

- **Caching**: Redis for frequently accessed data
- **Pagination**: Limit query results
- **Lazy Loading**: Load related data on demand
- **Query Optimization**: Use `select_related` for joins
- **Frontend**: React.memo, useMemo, useCallback

## Testing Strategy

### Unit Tests
- Test business logic in isolation
- Mock database operations
- Fast execution

### Integration Tests
- Test API endpoints end-to-end
- Use in-memory database
- Verify request/response contracts

### Frontend Tests
- Component rendering
- User interactions
- API mocking

## Deployment Architecture

### Development
```
Frontend (localhost:3000) → Backend (localhost:5000) → SQLite
```

### Production
```
Frontend (CDN/Static Host)
         ↓
    Load Balancer
         ↓
Backend Servers (Gunicorn + Flask)
         ↓
    PostgreSQL
```

## Monitoring & Observability

### Logging
- SQLAlchemy query logging (development)
- Flask request logging
- Error tracking (Sentry recommended)

### Metrics
- Request count/duration
- Database query performance
- Error rates
- Task status distribution

### Health Checks
- `/health` endpoint
- Database connectivity check
- API availability monitoring
