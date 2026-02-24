"""Unit tests for task service layer."""
import pytest
from app.models.task import Task, Status, Priority
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import (
    TaskService, TaskNotFoundError, InvalidStatusTransitionError
)


class TestTaskService:
    """Test TaskService business logic."""
    
    def test_create_task(self, db):
        """Test creating a new task."""
        data = TaskCreate(
            title="Test Task",
            description="Test Description",
            priority=Priority.HIGH
        )
        
        task = TaskService.create_task(data)
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == Priority.HIGH
        assert task.status == Status.PENDING
    
    def test_create_task_with_defaults(self, db):
        """Test creating task with default values."""
        data = TaskCreate(title="Test Task")
        
        task = TaskService.create_task(data)
        
        assert task.priority == Priority.MEDIUM
        assert task.status == Status.PENDING
        assert task.description is None
    
    def test_get_task_success(self, db):
        """Test retrieving existing task."""
        data = TaskCreate(title="Test Task")
        created = TaskService.create_task(data)
        
        retrieved = TaskService.get_task(created.id)
        
        assert retrieved.id == created.id
        assert retrieved.title == created.title
    
    def test_get_task_not_found(self, db):
        """Test retrieving non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            TaskService.get_task(999)
    
    def test_get_all_tasks(self, db):
        """Test retrieving all tasks."""
        TaskService.create_task(TaskCreate(title="Task 1"))
        TaskService.create_task(TaskCreate(title="Task 2"))
        TaskService.create_task(TaskCreate(title="Task 3"))
        
        tasks = TaskService.get_all_tasks()
        
        assert len(tasks) == 3
    
    def test_get_all_tasks_filtered_by_status(self, db):
        """Test filtering tasks by status."""
        task1 = TaskService.create_task(TaskCreate(title="Task 1"))
        task2 = TaskService.create_task(TaskCreate(title="Task 2"))
        
        # Update one task to IN_PROGRESS
        TaskService.update_task_status(task1.id, Status.IN_PROGRESS)
        
        pending_tasks = TaskService.get_all_tasks(status=Status.PENDING)
        in_progress_tasks = TaskService.get_all_tasks(status=Status.IN_PROGRESS)
        
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == task2.id
        assert len(in_progress_tasks) == 1
        assert in_progress_tasks[0].id == task1.id
    
    def test_get_all_tasks_filtered_by_priority(self, db):
        """Test filtering tasks by priority."""
        TaskService.create_task(TaskCreate(title="High", priority=Priority.HIGH))
        TaskService.create_task(TaskCreate(title="Low", priority=Priority.LOW))
        TaskService.create_task(TaskCreate(title="High 2", priority=Priority.HIGH))
        
        high_tasks = TaskService.get_all_tasks(priority=Priority.HIGH)
        low_tasks = TaskService.get_all_tasks(priority=Priority.LOW)
        
        assert len(high_tasks) == 2
        assert len(low_tasks) == 1
    
    def test_update_task(self, db):
        """Test updating task fields."""
        task = TaskService.create_task(TaskCreate(title="Original"))
        
        update_data = TaskUpdate(
            title="Updated",
            description="New description",
            priority=Priority.HIGH
        )
        
        updated = TaskService.update_task(task.id, update_data)
        
        assert updated.title == "Updated"
        assert updated.description == "New description"
        assert updated.priority == Priority.HIGH
    
    def test_update_task_partial(self, db):
        """Test partial update only changes specified fields."""
        task = TaskService.create_task(TaskCreate(
            title="Original",
            description="Original description",
            priority=Priority.LOW
        ))
        
        update_data = TaskUpdate(title="Updated")
        updated = TaskService.update_task(task.id, update_data)
        
        assert updated.title == "Updated"
        assert updated.description == "Original description"
        assert updated.priority == Priority.LOW
    
    def test_update_task_not_found(self, db):
        """Test updating non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            TaskService.update_task(999, TaskUpdate(title="Test"))
    
    def test_valid_status_transition_pending_to_in_progress(self, db):
        """Test valid transition from PENDING to IN_PROGRESS."""
        task = TaskService.create_task(TaskCreate(title="Test"))
        
        updated = TaskService.update_task_status(task.id, Status.IN_PROGRESS)
        
        assert updated.status == Status.IN_PROGRESS
    
    def test_valid_status_transition_in_progress_to_completed(self, db):
        """Test valid transition from IN_PROGRESS to COMPLETED."""
        task = TaskService.create_task(TaskCreate(title="Test"))
        TaskService.update_task_status(task.id, Status.IN_PROGRESS)
        
        updated = TaskService.update_task_status(task.id, Status.COMPLETED)
        
        assert updated.status == Status.COMPLETED
    
    def test_valid_status_transition_in_progress_to_pending(self, db):
        """Test valid rollback from IN_PROGRESS to PENDING."""
        task = TaskService.create_task(TaskCreate(title="Test"))
        TaskService.update_task_status(task.id, Status.IN_PROGRESS)
        
        updated = TaskService.update_task_status(task.id, Status.PENDING)
        
        assert updated.status == Status.PENDING
    
    def test_invalid_status_transition_pending_to_completed(self, db):
        """Test invalid transition from PENDING to COMPLETED."""
        task = TaskService.create_task(TaskCreate(title="Test"))
        
        with pytest.raises(InvalidStatusTransitionError):
            TaskService.update_task_status(task.id, Status.COMPLETED)
    
    def test_invalid_status_transition_completed_to_any(self, db):
        """Test that COMPLETED is a terminal state."""
        task = TaskService.create_task(TaskCreate(title="Test"))
        TaskService.update_task_status(task.id, Status.IN_PROGRESS)
        TaskService.update_task_status(task.id, Status.COMPLETED)
        
        with pytest.raises(InvalidStatusTransitionError):
            TaskService.update_task_status(task.id, Status.PENDING)
        
        with pytest.raises(InvalidStatusTransitionError):
            TaskService.update_task_status(task.id, Status.IN_PROGRESS)
    
    def test_delete_task(self, db):
        """Test deleting a task."""
        task = TaskService.create_task(TaskCreate(title="Test"))
        task_id = task.id
        
        TaskService.delete_task(task_id)
        
        with pytest.raises(TaskNotFoundError):
            TaskService.get_task(task_id)
    
    def test_delete_task_not_found(self, db):
        """Test deleting non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            TaskService.delete_task(999)
