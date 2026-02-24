/**
 * Component for filtering tasks by status and priority.
 */

import React from 'react';
import { Status, Priority } from '../types/Task';

interface FilterBarProps {
  statusFilter: Status | 'ALL';
  priorityFilter: Priority | 'ALL';
  onStatusFilterChange: (status: Status | 'ALL') => void;
  onPriorityFilterChange: (priority: Priority | 'ALL') => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  statusFilter,
  priorityFilter,
  onStatusFilterChange,
  onPriorityFilterChange,
}) => {
  return (
    <div className="filter-bar">
      <div className="filter-group">
        <label htmlFor="status-filter">Status:</label>
        <select
          id="status-filter"
          value={statusFilter}
          onChange={(e) => onStatusFilterChange(e.target.value as Status | 'ALL')}
        >
          <option value="ALL">All</option>
          <option value={Status.PENDING}>Pending</option>
          <option value={Status.IN_PROGRESS}>In Progress</option>
          <option value={Status.COMPLETED}>Completed</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="priority-filter">Priority:</label>
        <select
          id="priority-filter"
          value={priorityFilter}
          onChange={(e) => onPriorityFilterChange(e.target.value as Priority | 'ALL')}
        >
          <option value="ALL">All</option>
          <option value={Priority.LOW}>Low</option>
          <option value={Priority.MEDIUM}>Medium</option>
          <option value={Priority.HIGH}>High</option>
        </select>
      </div>
    </div>
  );
};

export default FilterBar;
