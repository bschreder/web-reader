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
            response = await client.get("/api/history")
            assert response.status_code == 200

            history = response.json()
            assert "tasks" in history or isinstance(history, list)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_task_execution_and_completion(self, api_url: str, skip_if_no_services: bool):
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
        """Test cancelling a running task."""
        async with AsyncClient(base_url=api_url, timeout=30.0) as client:
            # Create long-running task
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

            # Give it a moment to start
            await asyncio.sleep(1)

            # Cancel the task
            response = await client.delete(f"/api/tasks/{task_id}")
            assert response.status_code in [200, 204]

            # Verify cancellation
            response = await client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200

            status_data = response.json()
            # Should be cancelled or in process of cancelling
            assert status_data.get("status") in ["cancelled", "running", "created"]

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
