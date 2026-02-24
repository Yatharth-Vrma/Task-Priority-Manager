# Quick Start Guide

## Get Running in 5 Minutes

### Prerequisites
- Python 3.9+
- Node.js 16+

### Backend (Terminal 1)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

✅ Backend running at http://localhost:5000

### Frontend (Terminal 2)

```bash
cd frontend
npm install
npm start
```

✅ Frontend running at http://localhost:3000

### Verify Setup

Open http://localhost:3000 in your browser. You should see the Task Priority Manager interface.

### Run Tests

```bash
cd backend
pytest tests/ -v
```

All tests should pass ✅

## Project Structure

```
task-manager/
├── backend/              # Flask API
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic validation
│   │   ├── services/    # Business logic
│   │   └── routes/      # API endpoints
│   ├── tests/           # Automated tests
│   └── run.py           # Entry point
├── frontend/            # React app
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── package.json
└── docs/                # Documentation
    ├── ARCHITECTURE.md
    ├── SETUP.md
    ├── WALKTHROUGH_SCRIPT.md
    ├── claude-guidance.md
    └── SUBMISSION_CHECKLIST.md
```

## Key Features

- ✅ Create tasks with title, description, priority
- ✅ Update task details
- ✅ Progress through workflow: PENDING → IN_PROGRESS → COMPLETED
- ✅ Filter by status and priority
- ✅ Delete tasks
- ✅ Invalid state transitions prevented

## API Endpoints

- `GET /api/tasks` - List all tasks
- `GET /api/tasks/:id` - Get task by ID
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `PUT /api/tasks/:id/status` - Update status
- `DELETE /api/tasks/:id` - Delete task

## Example API Usage

```bash
# Create a task
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete assessment",
    "description": "Build task manager",
    "priority": "HIGH"
  }'

# Get all tasks
curl http://localhost:5000/api/tasks

# Update status
curl -X PUT http://localhost:5000/api/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}'
```

## Documentation

- **README.md** - Project overview and technical decisions
- **docs/ARCHITECTURE.md** - Detailed architecture documentation
- **docs/SETUP.md** - Complete setup and deployment guide
- **docs/claude-guidance.md** - AI constraints and coding standards
- **docs/WALKTHROUGH_SCRIPT.md** - Video walkthrough script

## Next Steps

1. Read through README.md for architectural overview
2. Review docs/ARCHITECTURE.md for deep dive
3. Run the application and explore the UI
4. Run tests to see verification strategy
5. Review docs/WALKTHROUGH_SCRIPT.md for video recording guidance

## Questions?

See docs/SETUP.md for troubleshooting and detailed setup instructions.
