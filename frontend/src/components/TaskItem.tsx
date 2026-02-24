/**
 * Component for displaying a single task with inline actions.
 * Actions reveal on hover for a clean, uncluttered look.
 */

import React, { useState } from 'react';
import { Task, Status } from '../types/Task';

interface TaskItemProps {
  task: Task;
  onStatusChange: (id: number, status: Status) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onStatusChange, onDelete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStatusChange = async (newStatus: Status) => {
    setLoading(true);
    setError(null);
    try {
      await onStatusChange(task.id, newStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this task? This cannot be undone.')) return;
    setLoading(true);
    setError(null);
    try {
      await onDelete(task.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    } finally {
      setLoading(false);
    }
  };

  const isCompleted = task.status === Status.COMPLETED;
  const priorityClass = task.priority.toLowerCase();
  const statusClass = task.status.toLowerCase();

  return (
    <div className={`task-item${isCompleted ? ' completed' : ''}`}>
      {/* Priority bar */}
      <div className={`priority-indicator ${priorityClass}`} />

      {/* Content */}
      <div className="task-content">
        <div className="task-title-row">
          <span className="task-title">{task.title}</span>
          <span className={`badge badge-priority ${priorityClass}`}>
            {task.priority}
          </span>
        </div>

        {task.description && (
          <p className="task-description">{task.description}</p>
        )}

        <div className="task-meta">
          <span className={`badge badge-status ${statusClass}`}>
            {task.status.replace('_', ' ')}
          </span>
          <span className="task-date">
            {new Date(task.created_at).toLocaleDateString(undefined, {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </span>
        </div>

        {error && <div className="error-message" style={{ marginTop: '0.5rem' }}>{error}</div>}
      </div>

      {/* Actions */}
      <div className="task-actions">
        {task.status === Status.PENDING && (
          <button
            onClick={() => handleStatusChange(Status.IN_PROGRESS)}
            disabled={loading}
            className="btn btn-success btn-sm"
            title="Start working"
          >
            Start
          </button>
        )}

        {task.status === Status.IN_PROGRESS && (
          <>
            <button
              onClick={() => handleStatusChange(Status.COMPLETED)}
              disabled={loading}
              className="btn btn-success btn-sm"
              title="Mark as complete"
            >
              Complete
            </button>
            <button
              onClick={() => handleStatusChange(Status.PENDING)}
              disabled={loading}
              className="btn btn-warning btn-sm"
              title="Move back to pending"
            >
              Rollback
            </button>
          </>
        )}

        <button
          onClick={handleDelete}
          disabled={loading}
          className="btn btn-danger-outline btn-sm"
          title="Delete task"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default TaskItem;
