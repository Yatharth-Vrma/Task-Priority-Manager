"""Integration tests for task API endpoints."""
import pytest


class TestTaskAPI:
    """Test task API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
    
    def test_create_task_success(self, client):
        """Test creating a task via API."""
        response = client.post('/api/tasks', json={
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 'HIGH'
        })
        
        assert response.status_code == 201
        data = response.json
        assert data['title'] == 'Test Task'
        assert data['description'] == 'Test Description'
        assert data['priority'] == 'HIGH'
        assert data['status'] == 'PENDING'
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_create_task_with_defaults(self, client):
        """Test creating task with minimal data."""
        response = client.post('/api/tasks', json={
            'title': 'Minimal Task'
        })
        
        assert response.status_code == 201
        data = response.json
        assert data['title'] == 'Minimal Task'
        assert data['priority'] == 'MEDIUM'
        assert data['description'] is None
    
    def test_create_task_empty_title(self, client):
        """Test creating task with empty title fails."""
        response = client.post('/api/tasks', json={
            'title': '   '
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_create_task_missing_title(self, client):
        """Test creating task without title fails."""
        response = client.post('/api/tasks', json={
            'description': 'No title'
        })
        
        assert response.status_code == 400
    
    def test_create_task_invalid_priority(self, client):
        """Test creating task with invalid priority fails."""
        response = client.post('/api/tasks', json={
            'title': 'Test',
            'priority': 'INVALID'
        })
        
        assert response.status_code == 400
    
    def test_get_all_tasks_empty(self, client):
        """Test getting tasks when none exist."""
        response = client.get('/api/tasks')
        
        assert response.status_code == 200
        assert response.json == []
    
    def test_get_all_tasks(self, client):
        """Test getting all tasks."""
        client.post('/api/tasks', json={'title': 'Task 1'})
        client.post('/api/tasks', json={'title': 'Task 2'})
        client.post('/api/tasks', json={'title': 'Task 3'})
        
        response = client.get('/api/tasks')
        
        assert response.status_code == 200
        assert len(response.json) == 3
    
    def test_get_tasks_filtered_by_status(self, client):
        """Test filtering tasks by status."""
        # Create tasks
        resp1 = client.post('/api/tasks', json={'title': 'Task 1'})
        task1_id = resp1.json['id']
        client.post('/api/tasks', json={'title': 'Task 2'})
        
        # Update one to IN_PROGRESS
        client.put(f'/api/tasks/{task1_id}/status', json={'status': 'IN_PROGRESS'})
        
        # Filter by PENDING
        response = client.get('/api/tasks?status=PENDING')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Task 2'
        
        # Filter by IN_PROGRESS
        response = client.get('/api/tasks?status=IN_PROGRESS')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Task 1'
    
    def test_get_tasks_filtered_by_priority(self, client):
        """Test filtering tasks by priority."""
        client.post('/api/tasks', json={'title': 'High', 'priority': 'HIGH'})
        client.post('/api/tasks', json={'title': 'Low', 'priority': 'LOW'})
        
        response = client.get('/api/tasks?priority=HIGH')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'High'
    
    def test_get_task_by_id(self, client):
        """Test getting specific task."""
        create_response = client.post('/api/tasks', json={'title': 'Test Task'})
        task_id = create_response.json['id']
        
        response = client.get(f'/api/tasks/{task_id}')
        
        assert response.status_code == 200
        assert response.json['id'] == task_id
        assert response.json['title'] == 'Test Task'
    
    def test_get_task_not_found(self, client):
        """Test getting non-existent task."""
        response = client.get('/api/tasks/999')
        
        assert response.status_code == 404
        assert 'error' in response.json
    
    def test_update_task(self, client):
        """Test updating task."""
        create_response = client.post('/api/tasks', json={'title': 'Original'})
        task_id = create_response.json['id']
        
        response = client.put(f'/api/tasks/{task_id}', json={
            'title': 'Updated',
            'description': 'New description',
            'priority': 'HIGH'
        })
        
        assert response.status_code == 200
        data = response.json
        assert data['title'] == 'Updated'
        assert data['description'] == 'New description'
        assert data['priority'] == 'HIGH'
    
    def test_update_task_partial(self, client):
        """Test partial task update."""
        create_response = client.post('/api/tasks', json={
            'title': 'Original',
            'description': 'Original desc',
            'priority': 'LOW'
        })
        task_id = create_response.json['id']
        
        response = client.put(f'/api/tasks/{task_id}', json={
            'title': 'Updated'
        })
        
        assert response.status_code == 200
        data = response.json
        assert data['title'] == 'Updated'
        assert data['description'] == 'Original desc'
        assert data['priority'] == 'LOW'
    
    def test_update_task_not_found(self, client):
        """Test updating non-existent task."""
        response = client.put('/api/tasks/999', json={'title': 'Test'})
        
        assert response.status_code == 404
    
    def test_update_task_empty_title(self, client):
        """Test updating task with empty title fails."""
        create_response = client.post('/api/tasks', json={'title': 'Original'})
        task_id = create_response.json['id']
        
        response = client.put(f'/api/tasks/{task_id}', json={'title': '  '})
        
        assert response.status_code == 400
    
    def test_update_status_valid_transition(self, client):
        """Test valid status transition."""
        create_response = client.post('/api/tasks', json={'title': 'Test'})
        task_id = create_response.json['id']
        
        response = client.put(f'/api/tasks/{task_id}/status', json={
            'status': 'IN_PROGRESS'
        })
        
        assert response.status_code == 200
        assert response.json['status'] == 'IN_PROGRESS'
    
    def test_update_status_invalid_transition(self, client):
        """Test invalid status transition."""
        create_response = client.post('/api/tasks', json={'title': 'Test'})
        task_id = create_response.json['id']
        
        response = client.put(f'/api/tasks/{task_id}/status', json={
            'status': 'COMPLETED'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_update_status_not_found(self, client):
        """Test updating status of non-existent task."""
        response = client.put('/api/tasks/999/status', json={'status': 'IN_PROGRESS'})
        
        assert response.status_code == 404
    
    def test_delete_task(self, client):
        """Test deleting task."""
        create_response = client.post('/api/tasks', json={'title': 'Test'})
        task_id = create_response.json['id']
        
        response = client.delete(f'/api/tasks/{task_id}')
        
        assert response.status_code == 204
        
        # Verify task is gone
        get_response = client.get(f'/api/tasks/{task_id}')
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self, client):
        """Test deleting non-existent task."""
        response = client.delete('/api/tasks/999')
        
        assert response.status_code == 404
    
    def test_complete_workflow(self, client):
        """Test complete task lifecycle."""
        # Create task
        create_resp = client.post('/api/tasks', json={
            'title': 'Complete workflow test',
            'priority': 'HIGH'
        })
        assert create_resp.status_code == 201
        task_id = create_resp.json['id']
        
        # Start working on it
        update_resp = client.put(f'/api/tasks/{task_id}/status', json={
            'status': 'IN_PROGRESS'
        })
        assert update_resp.status_code == 200
        assert update_resp.json['status'] == 'IN_PROGRESS'
        
        # Complete it
        complete_resp = client.put(f'/api/tasks/{task_id}/status', json={
            'status': 'COMPLETED'
        })
        assert complete_resp.status_code == 200
        assert complete_resp.json['status'] == 'COMPLETED'
        
        # Verify it's in completed list
        list_resp = client.get('/api/tasks?status=COMPLETED')
        assert list_resp.status_code == 200
        assert len(list_resp.json) == 1
        assert list_resp.json[0]['id'] == task_id


class TestEdgeCases:
    """Edge-case and robustness tests."""

    def test_create_task_no_json_body(self, client):
        """POST with no body at all should return 400."""
        response = client.post('/api/tasks', content_type='application/json')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_create_task_malformed_json(self, client):
        """POST with invalid JSON string should return 400."""
        response = client.post(
            '/api/tasks',
            data='not-json',
            content_type='application/json',
        )
        assert response.status_code == 400

    def test_create_task_extra_fields_rejected(self, client):
        """Extra/unknown fields should be rejected (extra='forbid')."""
        response = client.post('/api/tasks', json={
            'title': 'Valid',
            'unknown_field': 'surprise',
        })
        assert response.status_code == 400
        assert 'error' in response.json

    def test_create_task_title_at_max_length(self, client):
        """Title at exactly 200 chars should succeed."""
        long_title = 'A' * 200
        response = client.post('/api/tasks', json={'title': long_title})
        assert response.status_code == 201
        assert response.json['title'] == long_title

    def test_create_task_title_over_max_length(self, client):
        """Title exceeding 200 chars should fail."""
        response = client.post('/api/tasks', json={'title': 'A' * 201})
        assert response.status_code == 400

    def test_create_task_description_at_max_length(self, client):
        """Description at exactly 1000 chars should succeed."""
        long_desc = 'B' * 1000
        response = client.post('/api/tasks', json={
            'title': 'Test',
            'description': long_desc,
        })
        assert response.status_code == 201
        assert response.json['description'] == long_desc

    def test_create_task_description_over_max_length(self, client):
        """Description exceeding 1000 chars should fail."""
        response = client.post('/api/tasks', json={
            'title': 'Test',
            'description': 'B' * 1001,
        })
        assert response.status_code == 400

    def test_update_task_no_json_body(self, client):
        """PUT update with no body should return 400."""
        resp = client.post('/api/tasks', json={'title': 'Test'})
        task_id = resp.json['id']

        response = client.put(
            f'/api/tasks/{task_id}',
            content_type='application/json',
        )
        assert response.status_code == 400

    def test_update_task_extra_fields_rejected(self, client):
        """Extra fields on update should be rejected."""
        resp = client.post('/api/tasks', json={'title': 'Test'})
        task_id = resp.json['id']

        response = client.put(f'/api/tasks/{task_id}', json={
            'title': 'Updated',
            'foo': 'bar',
        })
        assert response.status_code == 400

    def test_status_update_no_json_body(self, client):
        """Status update with no body should return 400."""
        resp = client.post('/api/tasks', json={'title': 'Test'})
        task_id = resp.json['id']

        response = client.put(
            f'/api/tasks/{task_id}/status',
            content_type='application/json',
        )
        assert response.status_code == 400

    def test_status_update_extra_fields_rejected(self, client):
        """Extra fields on status update should be rejected."""
        resp = client.post('/api/tasks', json={'title': 'Test'})
        task_id = resp.json['id']

        response = client.put(f'/api/tasks/{task_id}/status', json={
            'status': 'IN_PROGRESS',
            'note': 'unexpected',
        })
        assert response.status_code == 400

    def test_filter_invalid_status(self, client):
        """Invalid status filter should return 400."""
        response = client.get('/api/tasks?status=INVALID_STATUS')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_filter_invalid_priority(self, client):
        """Invalid priority filter should return 400."""
        response = client.get('/api/tasks?priority=URGENT')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_completed_is_terminal(self, client):
        """Completed tasks cannot transition to any other state."""
        resp = client.post('/api/tasks', json={'title': 'Test'})
        task_id = resp.json['id']
        client.put(f'/api/tasks/{task_id}/status', json={'status': 'IN_PROGRESS'})
        client.put(f'/api/tasks/{task_id}/status', json={'status': 'COMPLETED'})

        for target in ('PENDING', 'IN_PROGRESS'):
            response = client.put(f'/api/tasks/{task_id}/status', json={'status': target})
            assert response.status_code == 400

    def test_rollback_in_progress_to_pending(self, client):
        """IN_PROGRESS → PENDING rollback should be allowed."""
        resp = client.post('/api/tasks', json={'title': 'Rollback'})
        task_id = resp.json['id']
        client.put(f'/api/tasks/{task_id}/status', json={'status': 'IN_PROGRESS'})

        response = client.put(f'/api/tasks/{task_id}/status', json={'status': 'PENDING'})
        assert response.status_code == 200
        assert response.json['status'] == 'PENDING'

    def test_create_task_whitespace_description_normalised(self, client):
        """Whitespace-only description should be stored as null."""
        response = client.post('/api/tasks', json={
            'title': 'Test',
            'description': '   ',
        })
        assert response.status_code == 201
        assert response.json['description'] is None

    def test_create_task_title_stripped(self, client):
        """Leading/trailing whitespace in title should be stripped."""
        response = client.post('/api/tasks', json={
            'title': '  Trimmed  ',
        })
        assert response.status_code == 201
        assert response.json['title'] == 'Trimmed'
