"""Pytest configuration and fixtures."""
import pytest
from app import create_app
from app.database import db as _db


@pytest.fixture(scope='function')
def app():
    """Create Flask application for testing."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """Provide database session for tests."""
    with app.app_context():
        yield _db
