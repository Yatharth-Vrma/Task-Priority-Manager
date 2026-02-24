"""Database configuration and initialization."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Import models to ensure they're registered
        from app.models.task import Task
        
        # Create all tables
        db.create_all()
