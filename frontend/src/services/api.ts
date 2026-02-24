/**
 * API service for task operations.
 * Centralizes all HTTP communication with backend.
 */

import { Task, TaskCreate, TaskUpdate, Priority, Status } from '../types/Task';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ApiError extends Error {
  constructor(public status: number, message: string, public details?: Record<string, unknown>[]) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Handle API response and extract JSON or throw error.
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new ApiError(response.status, error.error || 'Request failed', error.details);
  }
  
  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }
  
  return response.json();
}

export const taskApi = {
  /**
   * Get all tasks with optional filters.
   */
  async getAllTasks(filters?: { status?: Status; priority?: Priority }): Promise<Task[]> {
    const params = new URLSearchParams();
    
    if (filters?.status) {
      params.append('status', filters.status);
    }
    if (filters?.priority) {
      params.append('priority', filters.priority);
    }
    
    const url = `${API_BASE_URL}/tasks${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse<Task[]>(response);
  },

  /**
   * Get task by ID.
   */
  async getTask(id: number): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`);
    return handleResponse<Task>(response);
  },

  /**
   * Create a new task.
   */
  async createTask(data: TaskCreate): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse<Task>(response);
  },

  /**
   * Update task details.
   */
  async updateTask(id: number, data: TaskUpdate): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse<Task>(response);
  },

  /**
   * Update task status.
   */
  async updateTaskStatus(id: number, status: Status): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    return handleResponse<Task>(response);
  },

  /**
   * Delete a task.
   */
  async deleteTask(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(response);
  },
};

export { ApiError };
