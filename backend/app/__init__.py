"""Flask application factory."""
import os
import logging
from flask import Flask, request as flask_request
from flask_cors import CORS

from app.database import init_db
from app.routes.tasks import tasks_bp

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Create and configure Flask application.
    
    Args:
        test_config: Optional configuration for testing
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            'sqlite:///tasks.db'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config.update(test_config)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(tasks_bp)
    
    # Request/response logging
    @app.before_request
    def log_request():
        if flask_request.path != '/health':
            logger.info("→ %s %s", flask_request.method, flask_request.path)
    
    @app.after_request
    def log_response(response):
        if flask_request.path != '/health':
            logger.info("← %s %s %d", flask_request.method, flask_request.path, response.status_code)
        return response
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app
