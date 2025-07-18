"""
Integration tests for API endpoints.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from spec_driven_agent.agents.agent_manager import AgentManager
from spec_driven_agent.main import app
from spec_driven_agent.models.task import Task, TaskStatus
from tests.utils.test_helpers import TestAssertions, TestDataFactory


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def agent_manager(self):
        """Create an agent manager with test agents."""
        manager = AgentManager()

        # Register test agents
        from spec_driven_agent.agents.analyst_agent import AnalystAgent
        from spec_driven_agent.agents.product_manager_agent import ProductManagerAgent

        analyst = AnalystAgent(
            agent_id="analyst-001",
            name="Test Analyst",
            description="A test analyst agent",
        )

        pm = ProductManagerAgent(
            agent_id="pm-001",
            name="Test Product Manager",
            description="A test product manager agent",
        )

        manager.register_agent(analyst)
        manager.register_agent(pm)

        return manager

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert data["name"] == "Spec-Driven Agent Workflow"

    def test_health_endpoint(self, client):
        """Test the health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_list_agents_endpoint(self, client, agent_manager):
        """Test listing agents endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            response = client.get("/api/v1/agents")

            assert response.status_code == 200
            data = response.json()
            assert "agents" in data
            assert len(data["agents"]) == 2

            # Check agent details
            agent_ids = [agent["id"] for agent in data["agents"]]
            assert "analyst-001" in agent_ids
            assert "pm-001" in agent_ids

    def test_get_agent_endpoint(self, client, agent_manager):
        """Test getting specific agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            response = client.get("/api/v1/agents/analyst-001")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "analyst-001"
            assert data["name"] == "Test Analyst"
            assert data["agent_type"] == "analyst"
            assert data["status"] == "active"

    def test_get_nonexistent_agent_endpoint(self, client, agent_manager):
        """Test getting non-existent agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            response = client.get("/api/v1/agents/non-existent")

            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "not found" in data["error"].lower()

    def test_ping_agent_endpoint(self, client, agent_manager):
        """Test pinging agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            response = client.post("/api/v1/agents/analyst-001/ping")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["agent_id"] == "analyst-001"
            assert "message" in data
            assert "timestamp" in data

    def test_ping_nonexistent_agent_endpoint(self, client, agent_manager):
        """Test pinging non-existent agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            response = client.post("/api/v1/agents/non-existent/ping")

            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "not found" in data["error"].lower()

    def test_assign_task_endpoint(self, client, agent_manager):
        """Test assigning task to agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            task_data = {
                "name": "Test Requirements Task",
                "description": "Gather requirements for test project",
                "task_type": "requirements_gathering",
                "priority": "high",
                "estimated_hours": 8.0,
                "project_id": "project-001",
                "workflow_id": "workflow-001",
                "context": {"domain": "e-commerce"},
            }

            response = client.post("/api/v1/agents/analyst-001/tasks", json=task_data)

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "completed"
            assert "result" in data
            assert "artifacts" in data
            assert "metadata" in data

    def test_assign_task_to_nonexistent_agent_endpoint(self, client, agent_manager):
        """Test assigning task to non-existent agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            task_data = {
                "name": "Test Task",
                "description": "A test task",
                "task_type": "requirements_gathering",
                "priority": "medium",
                "estimated_hours": 4.0,
                "project_id": "project-001",
                "workflow_id": "workflow-001",
                "context": {},
            }

            response = client.post("/api/v1/agents/non-existent/tasks", json=task_data)

            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "not found" in data["error"].lower()

    def test_assign_invalid_task_endpoint(self, client, agent_manager):
        """Test assigning invalid task to agent endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            # Missing required fields
            task_data = {
                "name": "Invalid Task",
                # Missing description, task_type, etc.
            }

            response = client.post("/api/v1/agents/analyst-001/tasks", json=task_data)

            assert response.status_code == 422  # Validation error

    def test_system_status_endpoint(self, client, agent_manager):
        """Test system status endpoint."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            response = client.get("/api/v1/system/status")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "agents" in data
            assert "uptime" in data
            assert "version" in data

    def test_assign_task_to_product_manager_endpoint(self, client, agent_manager):
        """Test assigning PRD creation task to product manager."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            task_data = {
                "name": "Create PRD",
                "description": "Create product requirements document",
                "task_type": "prd_creation",
                "priority": "high",
                "estimated_hours": 12.0,
                "project_id": "project-001",
                "workflow_id": "workflow-001",
                "context": {"requirements": "gathered"},
            }

            response = client.post("/api/v1/agents/pm-001/tasks", json=task_data)

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "completed"
            assert "result" in data
            assert "artifacts" in data

    def test_assign_unsupported_task_endpoint(self, client, agent_manager):
        """Test assigning unsupported task type to agent."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            # Try to assign PRD creation to analyst (not supported)
            task_data = {
                "name": "Create PRD",
                "description": "Create product requirements document",
                "task_type": "prd_creation",
                "priority": "high",
                "estimated_hours": 12.0,
                "project_id": "project-001",
                "workflow_id": "workflow-001",
                "context": {},
            }

            response = client.post("/api/v1/agents/analyst-001/tasks", json=task_data)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"
            assert "error" in data
            assert "unsupported" in data["error"].lower()

    def test_api_error_handling(self, client):
        """Test API error handling."""
        # Test invalid endpoint
        response = client.get("/api/v1/invalid/endpoint")
        assert response.status_code == 404

        # Test invalid method
        response = client.put("/api/v1/agents")
        assert response.status_code == 405  # Method not allowed

    def test_api_response_format_consistency(self, client, agent_manager):
        """Test that API responses have consistent format."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            # Test agents endpoint
            response = client.get("/api/v1/agents")
            assert response.status_code == 200
            data = response.json()

            # Check consistent structure
            assert "agents" in data
            assert isinstance(data["agents"], list)

            if data["agents"]:
                agent = data["agents"][0]
                required_fields = ["id", "name", "agent_type", "status", "capabilities"]
                for field in required_fields:
                    assert field in agent

    @pytest.mark.asyncio
    async def test_async_task_processing(self, client, agent_manager):
        """Test async task processing through API."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            task_data = {
                "name": "Async Test Task",
                "description": "Test async task processing",
                "task_type": "requirements_gathering",
                "priority": "medium",
                "estimated_hours": 4.0,
                "project_id": "project-001",
                "workflow_id": "workflow-001",
                "context": {"test": "async"},
            }

            response = client.post("/api/v1/agents/analyst-001/tasks", json=task_data)

            assert response.status_code == 200
            data = response.json()

            # Validate task result structure
            TestAssertions.assert_valid_task_result(data)

            # Check that the task was processed asynchronously
            assert "metadata" in data
            assert "processing_time" in data["metadata"]

    def test_concurrent_task_processing(self, client, agent_manager):
        """Test concurrent task processing."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            import asyncio

            import httpx

            async def send_concurrent_requests():
                async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
                    tasks = []
                    for i in range(3):
                        task_data = {
                            "name": f"Concurrent Task {i}",
                            "description": f"Test concurrent task {i}",
                            "task_type": "requirements_gathering",
                            "priority": "medium",
                            "estimated_hours": 2.0,
                            "project_id": f"project-{i}",
                            "workflow_id": f"workflow-{i}",
                            "context": {"test": f"concurrent-{i}"},
                        }

                        tasks.append(
                            ac.post("/api/v1/agents/analyst-001/tasks", json=task_data)
                        )

                    responses = await asyncio.gather(*tasks)
                    return responses

            # Run concurrent requests
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                responses = loop.run_until_complete(send_concurrent_requests())

                # All requests should succeed
                for response in responses:
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "completed"
            finally:
                loop.close()

    def test_api_performance(self, client, agent_manager):
        """Test API performance under load."""
        with patch("spec_driven_agent.main.agent_manager", agent_manager):
            import time

            # Test multiple requests
            start_time = time.time()

            for i in range(10):
                response = client.get("/api/v1/agents")
                assert response.status_code == 200

            end_time = time.time()
            total_time = end_time - start_time

            # Should complete within reasonable time (adjust as needed)
            assert total_time < 5.0, f"API too slow: {total_time}s for 10 requests"

            # Average response time should be reasonable
            avg_time = total_time / 10
            assert avg_time < 0.5, f"Average response time too high: {avg_time}s"
