/**
 * Component for rendering the list of tasks.
 * Shows a friendly empty state when no tasks exist.
 */

import React from 'react';
import { Task, Status } from '../types/Task';
import TaskItem from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onStatusChange: (id: number, status: Status) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onStatusChange, onDelete }) => {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📋</div>
        <p>No tasks yet</p>
        <p className="empty-hint">Click <strong>+ Add Task</strong> above to create your first task.</p>
      </div>
    );
  }

  return (
    <div className="task-list">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onStatusChange={onStatusChange}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

export default TaskList;
