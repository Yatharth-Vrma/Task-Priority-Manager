"""Task service containing business logic."""
import logging
from typing import List, Optional

from app.database import db
from app.models.task import Task, Status, Priority
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


class TaskNotFoundError(Exception):
    """Raised when task is not found."""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when attempting invalid status transition."""
    pass


class TaskService:
    """Service for task operations.
    
    Encapsulates business logic and database operations.
    Routes should call these methods rather than accessing database directly.
    """
    
    @staticmethod
    def create_task(data: TaskCreate) -> Task:
        """Create a new task.
        
        Args:
            data: Validated task creation data
            
        Returns:
            Created task instance
        """
        task = Task(
            title=data.title,
            description=data.description,
            priority=data.priority,
            status=Status.PENDING  # All new tasks start as PENDING
        )
        
        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)
        
        logger.info("Task created: id=%d title=%r priority=%s", task.id, task.title, task.priority.value)
        return task
    
    @staticmethod
    def get_task(task_id: int) -> Task:
        """Get task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task instance
            
        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = db.session.get(Task, task_id)
        if task is None:
            logger.warning("Task not found: id=%d", task_id)
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        return task
    
    @staticmethod
    def get_all_tasks(
        status: Optional[Status] = None,
        priority: Optional[Priority] = None
    ) -> List[Task]:
        """Get all tasks with optional filtering.
        
        Args:
            status: Optional status filter
            priority: Optional priority filter
            
        Returns:
            List of tasks matching criteria
        """
        query = db.session.query(Task)
        
        if status is not None:
            query = query.filter(Task.status == status)
        
        if priority is not None:
            query = query.filter(Task.priority == priority)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        logger.debug("Listed tasks: count=%d status=%s priority=%s", len(tasks), status, priority)
        return tasks
    
    @staticmethod
    def update_task(task_id: int, data: TaskUpdate) -> Task:
        """Update task details.
        
        Only updates fields that are provided (not None).
        
        Args:
            task_id: Task identifier
            data: Task update data
            
        Returns:
            Updated task instance
            
        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = TaskService.get_task(task_id)
        
        # Only update fields that were provided
        if data.title is not None:
            task.title = data.title
        
        if data.description is not None:
            task.description = data.description
        
        if data.priority is not None:
            task.priority = data.priority
        
        db.session.commit()
        db.session.refresh(task)
        
        logger.info("Task updated: id=%d fields=%s", task_id, 
                     [f for f in ('title', 'description', 'priority') if getattr(data, f) is not None])
        return task
    
    @staticmethod
    def update_task_status(task_id: int, new_status: Status) -> Task:
        """Update task status with transition validation.
        
        Enforces valid status transitions defined in Task model.
        
        Args:
            task_id: Task identifier
            new_status: Desired status
            
        Returns:
            Updated task instance
            
        Raises:
            TaskNotFoundError: If task doesn't exist
            InvalidStatusTransitionError: If transition is invalid
        """
        task = TaskService.get_task(task_id)
        
        if not Task.can_transition(task.status, new_status):
            raise InvalidStatusTransitionError(
                f"Cannot transition from {task.status.value} to {new_status.value}. "
                f"Valid transitions from {task.status.value} are: "
                f"{', '.join(s.value for s in _get_valid_transitions(task.status))}"
            )
        
        task.status = new_status
        db.session.commit()
        db.session.refresh(task)
        
        logger.info("Task status updated: id=%d status=%s", task_id, new_status.value)
        return task
    
    @staticmethod
    def delete_task(task_id: int) -> None:
        """Delete a task.
        
        Args:
            task_id: Task identifier
            
        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = TaskService.get_task(task_id)
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deleted: id=%d", task_id)


def _get_valid_transitions(from_status: Status) -> List[Status]:
    """Get list of valid transitions from a status.
    
    Helper function for error messages.
    
    Args:
        from_status: Current status
        
    Returns:
        List of valid target statuses
    """
    valid_transitions = {
        Status.PENDING: [Status.IN_PROGRESS],
        Status.IN_PROGRESS: [Status.COMPLETED, Status.PENDING],
        Status.COMPLETED: []
    }
    
    return valid_transitions.get(from_status, [])
