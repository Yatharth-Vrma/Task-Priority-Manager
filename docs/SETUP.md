# Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will be available at `http://localhost:3000`

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Environment Variables

### Backend

Create a `.env` file in the backend directory (optional):

```env
DATABASE_URL=sqlite:///tasks.db
FLASK_ENV=development
```

### Frontend

Create a `.env` file in the frontend directory (optional):

```env
REACT_APP_API_URL=http://localhost:5000/api
```

## Troubleshooting

### Port already in use

If port 5000 or 3000 is already in use:

**Backend:**
```bash
# Change port in run.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Frontend:**
```bash
# Set PORT environment variable
PORT=3001 npm start
```

### CORS Issues

If you encounter CORS issues, ensure:
1. Backend is running on port 5000
2. Frontend is accessing `http://localhost:5000/api`
3. CORS configuration in `app/__init__.py` allows your frontend origin

### Database Issues

If database is corrupted:
```bash
cd backend
rm tasks.db
python run.py  # Will recreate database
```

## Production Deployment

### Backend

1. Set environment to production:
```bash
export FLASK_ENV=production
```

2. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

3. Use PostgreSQL instead of SQLite:
```bash
export DATABASE_URL=postgresql://user:pass@localhost/taskdb
```

### Frontend

1. Build production bundle:
```bash
npm run build
```

2. Serve static files:
```bash
npm install -g serve
serve -s build -l 3000
```

Or deploy to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
