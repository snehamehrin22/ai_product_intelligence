"""
API endpoint tests
"""
import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint returns 200 and connection status"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data


class TestTaskCRUD:
    """Tests for task CRUD operations"""

    def test_create_task_success(self, client, sample_task):
        """Test creating a task returns 201 with task data"""
        response = client.post("/tasks", json=sample_task)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "task_id" in data
        assert data["title"] == sample_task["title"]
        assert data["description"] == sample_task["description"]
        assert data["status"] == sample_task["status"]
        assert data["priority"] == sample_task["priority"]
        assert data["user_id"] == sample_task["user_id"]

    def test_create_task_missing_title(self, client, test_user_id):
        """Test creating task without title returns 422 validation error"""
        invalid_task = {
            "user_id": test_user_id,
            "status": "pending",
            "priority": "medium"
        }
        response = client.post("/tasks", json=invalid_task)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_invalid_status(self, client, sample_task):
        """Test creating task with invalid status returns 422"""
        invalid_task = sample_task.copy()
        invalid_task["status"] = "invalid_status"
        response = client.post("/tasks", json=invalid_task)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_invalid_priority(self, client, sample_task):
        """Test creating task with invalid priority returns 422"""
        invalid_task = sample_task.copy()
        invalid_task["priority"] = "super_urgent"
        response = client.post("/tasks", json=invalid_task)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_tasks_list(self, client, test_user_id):
        """Test getting list of tasks returns 200 with tasks array"""
        response = client.get(f"/tasks?user_id={test_user_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_get_tasks_with_status_filter(self, client, test_user_id):
        """Test filtering tasks by status"""
        # Create a pending task
        task_data = {
            "user_id": test_user_id,
            "title": "Pending Task",
            "status": "pending",
            "priority": "low"
        }
        create_response = client.post("/tasks", json=task_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Query for pending tasks
        response = client.get(f"/tasks?user_id={test_user_id}&status=pending")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned tasks should have pending status
        for task in data["tasks"]:
            assert task["status"] == "pending"

    def test_get_single_task_success(self, client, sample_task):
        """Test getting single task by ID returns 200"""
        # Create a task first
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Get the task
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == task_id
        assert data["title"] == sample_task["title"]

    def test_get_single_task_not_found(self, client):
        """Test getting non-existent task returns 404"""
        response = client.get("/tasks/nonexistent-task-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_update_task_success(self, client, sample_task):
        """Test updating task returns 200 with updated data"""
        # Create a task first
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Update the task
        updates = {
            "title": "Updated Title",
            "status": "completed"
        }
        response = client.put(f"/tasks/{task_id}", json=updates)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "completed"

    def test_update_task_not_found(self, client):
        """Test updating non-existent task returns 404"""
        updates = {"title": "New Title"}
        response = client.put("/tasks/nonexistent-task-id", json=updates)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_partial(self, client, sample_task):
        """Test partial updates only change specified fields"""
        # Create a task
        create_response = client.post("/tasks", json=sample_task)
        original_task = create_response.json()
        task_id = original_task["task_id"]

        # Update only priority
        updates = {"priority": "urgent"}
        response = client.put(f"/tasks/{task_id}", json=updates)
        assert response.status_code == status.HTTP_200_OK
        updated_task = response.json()

        # Priority should change
        assert updated_task["priority"] == "urgent"
        # Other fields should remain the same
        assert updated_task["title"] == original_task["title"]
        assert updated_task["description"] == original_task["description"]

    def test_delete_task_success(self, client, sample_task):
        """Test deleting task returns 204"""
        # Create a task first
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Delete the task
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is gone
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_not_found(self, client):
        """Test deleting non-existent task returns 404"""
        response = client.delete("/tasks/nonexistent-task-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAgentEndpoint:
    """Tests for AI agent chat endpoint"""

    @pytest.mark.slow
    def test_agent_chat_simple_message(self, client, test_user_id):
        """Test agent chat processes message and creates task

        Note: This test calls OpenAI API and may be slow
        """
        message = "Remind me to buy groceries tomorrow"
        response = client.post(
            f"/agent/chat?message={message}&user_id={test_user_id}"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        # Agent should create a task
        assert data.get("task_created") is True
        assert "task_id" in data

    @pytest.mark.slow
    def test_agent_chat_with_priority(self, client, test_user_id):
        """Test agent extracts priority from message

        Note: This test calls OpenAI API and may be slow
        """
        message = "URGENT: Fix production bug immediately"
        response = client.post(
            f"/agent/chat?message={message}&user_id={test_user_id}"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_created"] is True

        # Verify the created task has high/urgent priority
        task_id = data["task_id"]
        task_response = client.get(f"/tasks/{task_id}")
        task = task_response.json()
        assert task["priority"] in ["high", "urgent"]
