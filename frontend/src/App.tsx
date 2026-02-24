/**
 * Main application component.
 * Manages application state and coordinates child components.
 */

import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { Task, TaskCreate, Status, Priority } from './types/Task';
import { taskApi, ApiError } from './services/api';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import FilterBar from './components/FilterBar';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<Status | 'ALL'>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'ALL'>('ALL');
  const [showForm, setShowForm] = useState(false);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const filters: { status?: Status; priority?: Priority } = {};

      if (statusFilter !== 'ALL') {
        filters.status = statusFilter;
      }

      if (priorityFilter !== 'ALL') {
        filters.priority = priorityFilter;
      }

      const data = await taskApi.getAllTasks(filters);
      setTasks(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleCreateTask = async (data: TaskCreate) => {
    const newTask = await taskApi.createTask(data);
    setTasks((prev) => [newTask, ...prev]);
    setShowForm(false);
  };

  const handleStatusChange = async (id: number, status: Status) => {
    const updatedTask = await taskApi.updateTaskStatus(id, status);
    setTasks((prev) =>
      prev.map((task) => (task.id === id ? updatedTask : task))
    );
  };

  const handleDelete = async (id: number) => {
    await taskApi.deleteTask(id);
    setTasks((prev) => prev.filter((task) => task.id !== id));
  };

  /* Computed stats */
  const totalTasks = tasks.length;
  const pendingCount = tasks.filter((t) => t.status === Status.PENDING).length;
  const inProgressCount = tasks.filter((t) => t.status === Status.IN_PROGRESS).length;
  const completedCount = tasks.filter((t) => t.status === Status.COMPLETED).length;

  return (
    <div className="App">
      {/* ── Header ─────────────────────────────────── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <div className="logo-icon">T</div>
            <h1>Task Priority Manager</h1>
          </div>

          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-value">{totalTasks}</div>
              <div className="stat-label">Total</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{pendingCount}</div>
              <div className="stat-label">Pending</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{inProgressCount}</div>
              <div className="stat-label">Active</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{completedCount}</div>
              <div className="stat-label">Done</div>
            </div>
          </div>
        </div>
      </header>

      {/* ── Main ───────────────────────────────────── */}
      <main className="app-main">
        {/* Create Task Card */}
        <section className="card">
          <div className="card-header">
            <h2>New Task</h2>
            <button
              className="create-toggle-btn"
              onClick={() => setShowForm(!showForm)}
            >
              <span className="plus-icon">{showForm ? '−' : '+'}</span>
              {showForm ? 'Cancel' : 'Add Task'}
            </button>
          </div>

          {showForm && (
            <div className="card-body form-enter">
              <TaskForm
                onSubmit={handleCreateTask}
                onCancel={() => setShowForm(false)}
              />
            </div>
          )}
        </section>

        {/* Tasks Card */}
        <section className="card">
          <div className="card-header">
            <div className="section-header">
              <h2>Tasks {totalTasks > 0 && <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>({totalTasks})</span>}</h2>
            </div>
            <FilterBar
              statusFilter={statusFilter}
              priorityFilter={priorityFilter}
              onStatusFilterChange={setStatusFilter}
              onPriorityFilterChange={setPriorityFilter}
            />
          </div>

          <div className="card-body" style={{ padding: loading || error ? undefined : 0 }}>
            {loading ? (
              <div className="loading-state">
                <div className="spinner" />
                Loading tasks…
              </div>
            ) : error ? (
              <div className="error-state">
                <p>{error}</p>
                <button onClick={loadTasks} className="btn btn-primary">
                  Retry
                </button>
              </div>
            ) : (
              <TaskList
                tasks={tasks}
                onStatusChange={handleStatusChange}
                onDelete={handleDelete}
              />
            )}
          </div>
        </section>
      </main>

      {/* ── Footer ─────────────────────────────────── */}
      <footer className="app-footer">
        Task Priority Manager &middot; React + TypeScript &middot; Flask + SQLite
      </footer>
    </div>
  );
}

export default App;
