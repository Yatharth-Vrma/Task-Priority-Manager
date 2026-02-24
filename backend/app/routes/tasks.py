"""Task API routes."""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.task import (
    TaskCreate, TaskUpdate, StatusUpdate, 
    TaskResponse, ErrorResponse
)
from app.services.task_service import (
    TaskService, TaskNotFoundError, InvalidStatusTransitionError
)
from app.models.task import Status, Priority

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def serialize_pydantic_errors(errors):
    """Convert Pydantic validation errors to JSON-serializable format."""
    result = []
    for error in errors:
        serialized = {}
        for key, value in error.items():
            if key == 'ctx' and value:
                # Convert context error values to strings
                serialized[key] = {k: str(v) for k, v in value.items()}
            else:
                serialized[key] = value
        result.append(serialized)
    return result


@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering.
    
    Query Parameters:
        status: Filter by status (PENDING, IN_PROGRESS, COMPLETED)
        priority: Filter by priority (LOW, MEDIUM, HIGH)
    
    Returns:
        200: List of tasks
        400: Invalid query parameters
    """
    try:
        # Parse optional filters
        status = None
        if 'status' in request.args:
            status = Status(request.args['status'])
        
        priority = None
        if 'priority' in request.args:
            priority = Priority(request.args['priority'])
        
        tasks = TaskService.get_all_tasks(status=status, priority=priority)
        
        return jsonify([
            TaskResponse.model_validate(task).model_dump()
            for task in tasks
        ]), 200
    
    except ValueError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 400


@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id: int):
    """Get task by ID.
    
    Args:
        task_id: Task identifier
    
    Returns:
        200: Task details
        404: Task not found
    """
    try:
        task = TaskService.get_task(task_id)
        return jsonify(TaskResponse.model_validate(task).model_dump()), 200
    
    except TaskNotFoundError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 404


@tasks_bp.route('', methods=['POST'])
def create_task():
    """Create a new task.
    
    Request Body:
        title: Task title (required, 1-200 chars)
        description: Task description (optional, max 1000 chars)
        priority: Task priority (optional, default: MEDIUM)
    
    Returns:
        201: Created task
        400: Invalid request data
    """
    try:
        body = request.get_json(silent=True)
        if body is None:
            return jsonify(ErrorResponse(
                error="Request body must be valid JSON"
            ).model_dump()), 400

        data = TaskCreate(**body)
        task = TaskService.create_task(data)
        
        return jsonify(TaskResponse.model_validate(task).model_dump()), 201
    
    except ValidationError as e:
        return jsonify(ErrorResponse(
            error="Validation error",
            details=serialize_pydantic_errors(e.errors())
        ).model_dump()), 400
    
    except Exception as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 400


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id: int):
    """Update task details.
    
    Args:
        task_id: Task identifier
    
    Request Body:
        title: Task title (optional, 1-200 chars)
        description: Task description (optional, max 1000 chars)
        priority: Task priority (optional)
    
    Returns:
        200: Updated task
        400: Invalid request data
        404: Task not found
    """
    try:
        body = request.get_json(silent=True)
        if body is None:
            return jsonify(ErrorResponse(
                error="Request body must be valid JSON"
            ).model_dump()), 400

        data = TaskUpdate(**body)
        task = TaskService.update_task(task_id, data)
        
        return jsonify(TaskResponse.model_validate(task).model_dump()), 200
    
    except TaskNotFoundError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 404
    
    except ValidationError as e:
        return jsonify(ErrorResponse(
            error="Validation error",
            details=serialize_pydantic_errors(e.errors())
        ).model_dump()), 400
    
    except Exception as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 400


@tasks_bp.route('/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id: int):
    """Update task status.
    
    Args:
        task_id: Task identifier
    
    Request Body:
        status: New status (PENDING, IN_PROGRESS, COMPLETED)
    
    Returns:
        200: Updated task
        400: Invalid status or transition
        404: Task not found
    """
    try:
        body = request.get_json(silent=True)
        if body is None:
            return jsonify(ErrorResponse(
                error="Request body must be valid JSON"
            ).model_dump()), 400

        data = StatusUpdate(**body)
        task = TaskService.update_task_status(task_id, data.status)
        
        return jsonify(TaskResponse.model_validate(task).model_dump()), 200
    
    except TaskNotFoundError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 404
    
    except InvalidStatusTransitionError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 400
    
    except ValidationError as e:
        return jsonify(ErrorResponse(
            error="Validation error",
            details=serialize_pydantic_errors(e.errors())
        ).model_dump()), 400
    
    except Exception as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 400


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id: int):
    """Delete a task.
    
    Args:
        task_id: Task identifier
    
    Returns:
        204: Task deleted successfully
        404: Task not found
    """
    try:
        TaskService.delete_task(task_id)
        return '', 204
    
    except TaskNotFoundError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 404
