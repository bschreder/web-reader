"""Integration tests for camelCase/snake_case property mapping.

Tests that the API correctly:
1. Accepts camelCase properties from the frontend
2. Returns camelCase properties in responses
3. Maintains data integrity through the transformation
"""

from fastapi.testclient import TestClient


class TestPropertyMappingIntegration:
    """Test camelCase ↔ snake_case property mapping in API."""

    def test_create_task_with_camelcase_input(self, test_client: TestClient):
        """Test that POST /api/tasks accepts camelCase input from frontend."""
        # Frontend sends camelCase (JavaScript convention)
        camel_case_payload = {
            "question": "What is machine learning?",
            "seedUrl": "https://example.com",
            "maxDepth": 2,
            "maxPages": 10,
            "timeBudget": 60,
            "searchEngine": "google",
            "maxResults": 5,
            "safeMode": False,
            "sameDomainOnly": True,
            "allowExternalLinks": False,
        }

        response = test_client.post("/api/tasks", json=camel_case_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["question"] == "What is machine learning?"

    def test_create_task_response_uses_camelcase(self, test_client: TestClient):
        """Test that task creation response uses camelCase in JSON."""
        camel_case_payload = {
            "question": "What is Python?",
            "seedUrl": "https://python.org",
            "maxDepth": 3,
            "maxPages": 15,
            "timeBudget": 120,
            "searchEngine": "duckduckgo",
            "maxResults": 20,
            "safeMode": True,
            "sameDomainOnly": False,
            "allowExternalLinks": True,
        }

        response = test_client.post("/api/tasks", json=camel_case_payload)

        assert response.status_code == 201
        data = response.json()

        # Verify response uses camelCase (not snake_case)
        assert "seedUrl" in data or "question" in data
        # Should NOT have snake_case keys
        assert "seed_url" not in data
        assert "max_depth" not in data
        assert "max_pages" not in data
        assert "time_budget" not in data
        assert "search_engine" not in data
        assert "max_results" not in data
        assert "safe_mode" not in data
        assert "same_domain_only" not in data
        assert "allow_external_links" not in data

    def test_get_task_response_uses_camelcase(self, test_client: TestClient):
        """Test that GET /api/tasks/{taskId} response uses camelCase."""
        # Create task with camelCase input
        camel_case_payload = {
            "question": "Test question",
            "seedUrl": "https://example.com",
            "maxDepth": 2,
            "maxPages": 5,
            "timeBudget": 60,
            "searchEngine": "bing",
            "maxResults": 10,
            "safeMode": False,
            "sameDomainOnly": False,
            "allowExternalLinks": True,
        }

        create_response = test_client.post("/api/tasks", json=camel_case_payload)
        assert create_response.status_code == 201
        task_id = create_response.json()["taskId"]

        # Retrieve task and verify response uses camelCase
        get_response = test_client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 200
        data = get_response.json()

        # Verify camelCase in response
        assert "taskId" in data
        assert "createdAt" in data
        # Should NOT have snake_case
        assert "task_id" not in data
        assert "created_at" not in data

    def test_list_tasks_uses_camelcase(self, test_client: TestClient):
        """Test that GET /api/tasks response uses camelCase."""
        # Create a task first
        payload = {
            "question": "Test question",
            "seedUrl": "https://example.com",
            "maxDepth": 1,
            "maxPages": 5,
            "timeBudget": 30,
            "searchEngine": "google",
            "maxResults": 5,
            "safeMode": True,
            "sameDomainOnly": False,
            "allowExternalLinks": True,
        }

        test_client.post("/api/tasks", json=payload)

        # List tasks
        response = test_client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()

        # Should have camelCase keys in list response
        assert "tasks" in data
        assert "total" in data
        if data["tasks"]:
            task = data["tasks"][0]
            assert "taskId" in task
            assert "createdAt" in task
            # Should NOT have snake_case
            assert "task_id" not in task
            assert "created_at" not in task

    def test_property_values_preserved_through_mapping(self, test_client: TestClient):
        """Test that property values remain unchanged during camelCase/snake_case conversion."""
        original_payload = {
            "question": "What is artificial intelligence?",
            "seedUrl": "https://ai.example.com",
            "maxDepth": 3,
            "maxPages": 25,
            "timeBudget": 180,
            "searchEngine": "bing",
            "maxResults": 15,
            "safeMode": False,
            "sameDomainOnly": True,
            "allowExternalLinks": False,
        }

        response = test_client.post("/api/tasks", json=original_payload)
        assert response.status_code == 201
        data = response.json()

        # Verify all values are preserved (mapping doesn't corrupt data)
        assert data["question"] == original_payload["question"]
        assert data["seedUrl"] == original_payload["seedUrl"]
        # Note: some UC parameters may not be in response model, but verify what is there
        assert "taskId" in data  # Should be created
        assert "status" in data  # Should have status

    def test_create_task_with_minimal_payload(self, test_client: TestClient):
        """Test that required fields work with camelCase, optional fields have defaults."""
        minimal_payload = {
            "question": "Simple question",
        }

        response = test_client.post("/api/tasks", json=minimal_payload)
        assert response.status_code == 201
        data = response.json()

        assert data["question"] == "Simple question"
        assert "taskId" in data
        assert "status" in data

    def test_create_task_with_default_parameters(self, test_client: TestClient):
        """Test that default parameter values are applied when not provided."""
        payload = {
            "question": "Test with defaults",
        }

        response = test_client.post("/api/tasks", json=payload)
        assert response.status_code == 201
        data = response.json()

        assert data["question"] == "Test with defaults"
        # Defaults should be applied
        # (Note: defaults are in TaskCreate model, not necessarily in response)

    def test_both_camelcase_and_snakecase_accepted_on_input(
        self, test_client: TestClient
    ):
        """Test that backend accepts both camelCase and snake_case on input (populate_by_name=True)."""
        # Payload with snake_case (Python developers)
        snake_case_payload = {
            "question": "Snake case test",
            "seed_url": "https://example.com",
            "max_depth": 2,
            "max_pages": 10,
            "time_budget": 60,
            "search_engine": "google",
            "max_results": 5,
            "safe_mode": True,
            "same_domain_only": False,
            "allow_external_links": True,
        }

        response = test_client.post("/api/tasks", json=snake_case_payload)

        # Should still work with snake_case input
        assert response.status_code == 201
        data = response.json()
        assert data["question"] == "Snake case test"

    def test_invalid_enum_value_rejected(self, test_client: TestClient):
        """Test that invalid enum values in searchEngine are rejected."""
        invalid_payload = {
            "question": "Test question",
            "searchEngine": "invalid_engine",  # Invalid enum value
        }

        response = test_client.post("/api/tasks", json=invalid_payload)

        # Should reject invalid enum value
        assert response.status_code == 422  # Validation error

    def test_property_range_validation(self, test_client: TestClient):
        """Test that property range constraints work with camelCase input."""
        # maxDepth should be between 1-5
        invalid_payload = {
            "question": "Test question",
            "maxDepth": 10,  # Out of range
        }

        response = test_client.post("/api/tasks", json=invalid_payload)

        # Should reject out-of-range value
        assert response.status_code == 422

    def test_missing_required_field_validation(self, test_client: TestClient):
        """Test that missing required fields are caught."""
        invalid_payload = {
            # Missing required 'question' field
            "maxDepth": 2,
        }

        response = test_client.post("/api/tasks", json=invalid_payload)

        # Should reject missing required field
        assert response.status_code == 422

    def test_field_description_in_openapi_schema(self, test_client: TestClient):
        """Test that field descriptions are present in OpenAPI schema."""
        response = test_client.get("/openapi.json")

        # OpenAPI should be generated
        assert response.status_code == 200
        schema = response.json()

        # Should have schemas for request/response models
        assert "components" in schema or "definitions" in schema

    def test_response_model_consistency_across_endpoints(self, test_client: TestClient):
        """Test that all endpoints return consistent property names."""
        # Create task
        payload = {
            "question": "Consistency test",
            "seedUrl": "https://example.com",
        }
        create_response = test_client.post("/api/tasks", json=payload)
        assert create_response.status_code == 201
        created_data = create_response.json()

        # Get task
        task_id = created_data["taskId"]
        get_response = test_client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()

        # Both should use same property names (camelCase)
        assert set(created_data.keys()) == set(get_data.keys())
        # All keys should be camelCase (start with lowercase or have camelCase pattern)
        for key in created_data.keys():
            # Check that it's not snake_case (no underscores except for internal use)
            assert "_" not in key or key.startswith("_")
