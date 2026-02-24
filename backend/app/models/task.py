"""Task domain model with business rules and constraints."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from app.database import db
from sqlalchemy import CheckConstraint, Enum as SQLEnum


def _utcnow():
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Status(str, Enum):
    """Task status states."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task(db.Model):
    """Task model representing a single task in the system.
    
    Enforces constraints:
    - Title must not be empty
    - Priority must be valid enum value
    - Status must be valid enum value
    - Created/updated timestamps are automatic
    """
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM)
    status = db.Column(SQLEnum(Status), nullable=False, default=Status.PENDING)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=_utcnow,
        onupdate=_utcnow
    )
    
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name='title_not_empty'),
    )
    
    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.title} [{self.status.value}]>"
    
    def to_dict(self) -> dict:
        """Convert task to dictionary representation.
        
        Returns:
            Dictionary with all task fields
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def can_transition(from_status: Status, to_status: Status) -> bool:
        """Check if status transition is valid.
        
        Valid transitions:
        - PENDING → IN_PROGRESS
        - IN_PROGRESS → COMPLETED
        - IN_PROGRESS → PENDING (rollback)
        - COMPLETED → (no transitions, final state)
        
        Args:
            from_status: Current status
            to_status: Desired status
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            Status.PENDING: {Status.IN_PROGRESS},
            Status.IN_PROGRESS: {Status.COMPLETED, Status.PENDING},
            Status.COMPLETED: set()  # Terminal state
        }
        
        return to_status in valid_transitions.get(from_status, set())
