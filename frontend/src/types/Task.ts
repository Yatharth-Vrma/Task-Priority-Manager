/**
 * Type definitions matching backend schemas.
 * Ensures type safety across frontend-backend boundary.
 */

export enum Priority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
}

export enum Status {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: Priority;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: Priority;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: Priority;
}

export interface StatusUpdate {
  status: Status;
}

export interface ErrorResponse {
  error: string;
  details?: Record<string, unknown>[];
}
