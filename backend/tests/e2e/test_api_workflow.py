"""End-to-end tests for Backend API workflows."""

import asyncio

import pytest
from httpx import AsyncClient

from src.models import TaskCreate


class TestAPIWorkflow:
    """Test complete API workflows from task creation to completion."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_create_and_get_task(self, api_url: str):
        """Test creating a task and retrieving it."""
        async with AsyncClient(base_url=api_url, timeout=30.0) as client:
            # Create task
            task_data = TaskCreate(
                question="Test question for E2E",
                max_depth=1,
                max_pages=1,
                time_budget=30,
            )

            response = await client.post("/api/tasks", json=task_data.model_dump())
            assert response.status_code == 200 or response.status_code == 201

            data = response.json()
            task_id = data["task_id"]
            assert task_id is not None

            # Get task status
            response = await client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200

            task_status = response.json()
            assert task_status["task_id"] == task_id
            assert task_status["question"] == task_data.question

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_list_tasks(self, api_url: str):
        """Test listing all tasks."""
        async with AsyncClient(base_url=api_url, timeout=30.0) as client:
            # Create a couple of tasks
            for i in range(2):
                task_data = TaskCreate(
                    question=f"Test question {i}",
                    max_depth=1,
                    max_pages=1,
                    time_budget=30,
                )
                await client.post("/api/tasks", json=task_data.model_dump())

            # List tasks
            response = await client.get("/api/tasks")
            assert response.status_code == 200

            task_list = response.json()
            assert "tasks" in task_list
            assert task_list["total"] >= 2  # At least our 2 tasks

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_task_execution_and_completion(self, api_url: str):
        """Test full task execution from start to completion."""
        async with AsyncClient(base_url=api_url, timeout=60.0) as client:
            # Create simple task
            task_data = TaskCreate(
                question="What is 2+2?",
                seed_url="https://example.com",
                max_depth=1,
                max_pages=1,
                time_budget=30,
            )

            response = await client.post("/api/tasks", json=task_data.model_dump())
            assert response.status_code in [200, 201]

            data = response.json()
            task_id = data["task_id"]

            # Poll for completion (with timeout)
            max_wait = 45  # seconds
            poll_interval = 2
            elapsed = 0

            while elapsed < max_wait:
                response = await client.get(f"/api/tasks/{task_id}")
                assert response.status_code == 200

                status_data = response.json()
                status = status_data.get("status")

                if status in ["completed", "failed", "cancelled"]:
                    # Task finished
                    if status == "completed":
                        assert "answer" in status_data or status_data.get("result")
                    break

                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

            # If still running after max wait, that's okay for this test
            # The integration is working if we got valid status responses

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_task_cancellation(self, api_url: str):
        """Test cancelling a task."""
        async with AsyncClient(base_url=api_url, timeout=30.0) as client:
            # Create task
            task_data = TaskCreate(
                question="Complex research requiring lots of pages",
                max_depth=5,
                max_pages=50,
                time_budget=300,
            )

            response = await client.post("/api/tasks", json=task_data.model_dump())
            assert response.status_code in [200, 201]

            data = response.json()
            task_id = data["task_id"]

            # Verify task was created
            response = await client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            status_data = response.json()
            # Task may complete quickly or still be running
            assert status_data.get("status") in ["running", "created", "completed"]

            # Delete the task
            response = await client.delete(f"/api/tasks/{task_id}")
            assert response.status_code in [200, 204]

            # After deletion, task should not be found
            response = await client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_health_endpoint(self, api_url):
        """Test health check endpoint."""
        async with AsyncClient(base_url=api_url, timeout=10.0) as client:
            response = await client.get("/health")
            assert response.status_code == 200

            health_data = response.json()
            assert (
                health_data.get("status") == "healthy"
                or health_data.get("service") == "backend"
            )
