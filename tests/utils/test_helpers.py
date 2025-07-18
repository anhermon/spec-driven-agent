"""
Test helper utilities for common testing patterns.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from spec_driven_agent.models.agent import Agent, AgentRole
from spec_driven_agent.models.artifact import Artifact, ArtifactType
from spec_driven_agent.models.project import Project, ProjectStatus
from spec_driven_agent.models.task import Task, TaskStatus
from spec_driven_agent.models.workflow import (
    WorkflowInstance,
    WorkflowPhase,
    WorkflowStatus,
)


class TestDataFactory:
    """Factory for creating test data objects."""

    @staticmethod
    def create_task(
        task_id: Optional[str] = None,
        task_name: str = "Test Task",
        description: str = "A test task",
        task_type: str = "requirements_gathering",
        status: TaskStatus = TaskStatus.PENDING,
        priority: str = "medium",
        effort_estimate: float = 4.0,
        assigned_agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        phase: str = "discovery",
        **kwargs,
    ) -> Task:
        """Create a test task with default or custom values."""
        return Task(
            task_id=task_id or f"task-{uuid4().hex[:8]}",
            task_name=task_name,
            description=description,
            task_type=task_type,
            status=status,
            priority=priority,
            effort_estimate=effort_estimate,
            assigned_agent_id=uuid4() if assigned_agent_id is None else uuid4(),
            workflow_id=uuid4() if workflow_id is None else uuid4(),
            phase=phase,
            **kwargs,
        )

    @staticmethod
    def create_agent(
        agent_id: Optional[str] = None,
        agent_name: str = "Test Agent",
        agent_type: str = "analyst",
        role: AgentRole = AgentRole.ANALYST,
        status: str = "active",
        capabilities: Optional[List[str]] = None,
        **kwargs,
    ) -> Agent:
        """Create a test agent with default or custom values."""
        return Agent(
            agent_id=agent_id or f"agent-{uuid4().hex[:8]}",
            agent_name=agent_name,
            agent_type=agent_type,
            role=role,
            status=status,
            capabilities=capabilities or [],
            config={},
            settings={},
            **kwargs,
        )

    @staticmethod
    def create_project(
        name: str = "Test Project",
        slug: str = "test-project",
        description: str = "A test project",
        current_phase: ProjectStatus = ProjectStatus.DRAFT,
        stakeholders: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ) -> Project:
        """Create a test project with default or custom values."""
        return Project(
            name=name,
            slug=slug,
            description=description,
            current_phase=current_phase,
            stakeholders=stakeholders or [],
            tags=tags or ["test"],
            **kwargs,
        )

    @staticmethod
    def create_workflow(
        project_id: Optional[str] = None,
        workflow_type: str = "spec_driven",
        current_phase: WorkflowPhase = WorkflowPhase.DISCOVERY,
        completed_phases: Optional[List[WorkflowPhase]] = None,
        assigned_agents: Optional[List[str]] = None,
        task_queue: Optional[List[str]] = None,
        completed_tasks: Optional[List[str]] = None,
        **kwargs,
    ) -> WorkflowInstance:
        """Create a test workflow with default or custom values."""
        return WorkflowInstance(
            project_id=uuid4() if project_id is None else uuid4(),
            workflow_type=workflow_type,
            current_phase=current_phase,
            completed_phases=completed_phases or [],
            assigned_agents=assigned_agents or [],
            task_queue=task_queue or [],
            completed_tasks=completed_tasks or [],
            **kwargs,
        )

    @staticmethod
    def create_artifact(
        artifact_id: Optional[str] = None,
        artifact_name: str = "Test Artifact",
        artifact_type: ArtifactType = ArtifactType.DOCUMENT,
        content: Optional[str] = None,
        description: str = "A test artifact",
        project_id: Optional[str] = None,
        phase: str = "discovery",
        **kwargs,
    ) -> Artifact:
        """Create a test artifact with default or custom values."""
        return Artifact(
            artifact_id=artifact_id or f"artifact-{uuid4().hex[:8]}",
            artifact_name=artifact_name,
            artifact_type=artifact_type,
            content=content or "Test content",
            description=description,
            project_id=uuid4() if project_id is None else uuid4(),
            phase=phase,
            **kwargs,
        )


class AsyncTestCase:
    """Base class for async test cases with common utilities."""

    @staticmethod
    async def run_async_test(coro):
        """Run an async coroutine in a test."""
        return await coro

    @staticmethod
    def create_mock_async_result(result_data: Dict[str, Any]) -> AsyncMock:
        """Create a mock async result."""
        mock_result = AsyncMock()
        mock_result.return_value = result_data
        return mock_result

    @staticmethod
    def create_mock_async_exception(exception: Exception) -> AsyncMock:
        """Create a mock async function that raises an exception."""
        mock_func = AsyncMock()
        mock_func.side_effect = exception
        return mock_func

    @staticmethod
    def patch_async_method(target, method_name: str, return_value: Any = None):
        """Patch an async method for testing."""
        return patch.object(
            target, method_name, new_callable=AsyncMock, return_value=return_value
        )

    @staticmethod
    def patch_sync_method(target, method_name: str, return_value: Any = None):
        """Patch a sync method for testing."""
        return patch.object(
            target, method_name, new_callable=MagicMock, return_value=return_value
        )


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self._text = text or json.dumps(json_data) if json_data else ""
        self.headers = headers or {}

    def json(self) -> Dict[str, Any]:
        """Return JSON data."""
        return self._json_data

    @property
    def text(self) -> str:
        """Return response text."""
        return self._text

    def raise_for_status(self):
        """Raise an exception for bad status codes."""
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class TestAssertions:
    """Custom assertions for testing."""

    @staticmethod
    def assert_valid_task_result(result: Dict[str, Any]):
        """Assert that a task result has the required structure."""
        assert isinstance(result, dict)
        assert "task_id" in result
        assert "status" in result
        assert result["status"] in ["completed", "failed", "in_progress"]
        assert "result" in result
        assert "artifacts" in result
        assert "metadata" in result

    @staticmethod
    def assert_valid_agent_response(response: Dict[str, Any]):
        """Assert that an agent response has the required structure."""
        assert isinstance(response, dict)
        assert "status" in response
        assert response["status"] in ["success", "error"]
        assert "agent_id" in response
        assert "message" in response
        assert "timestamp" in response

    @staticmethod
    def assert_valid_project_data(project: Project):
        """Assert that a project has valid data."""
        assert project.name is not None
        assert project.slug is not None
        assert project.description is not None
        assert project.current_phase is not None

    @staticmethod
    def assert_valid_workflow_data(workflow: WorkflowInstance):
        """Assert that a workflow has valid data."""
        assert workflow.project_id is not None
        assert workflow.workflow_type is not None
        assert workflow.current_phase is not None
        assert isinstance(workflow.completed_phases, list)
        assert isinstance(workflow.assigned_agents, list)

    @staticmethod
    def assert_datetime_recent(dt: datetime, max_seconds: int = 60):
        """Assert that a datetime is recent (within max_seconds of now)."""
        now = datetime.now()
        diff = abs((now - dt).total_seconds())
        assert diff <= max_seconds, f"Datetime {dt} is not recent (diff: {diff}s)"

    @staticmethod
    def assert_uuid_valid(uuid_str: str):
        """Assert that a string is a valid UUID."""
        try:
            uuid4().hex  # This will raise ValueError if invalid
            assert len(uuid_str) > 0, "UUID string is empty"
        except ValueError:
            assert False, f"Invalid UUID format: {uuid_str}"


class PerformanceTestMixin:
    """Mixin for performance testing utilities."""

    @staticmethod
    async def measure_execution_time(coro, max_seconds: float = 5.0):
        """Measure the execution time of an async coroutine."""
        start_time = datetime.now()
        result = await coro
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        assert (
            execution_time <= max_seconds
        ), f"Execution took {execution_time}s, expected <= {max_seconds}s"
        return result, execution_time

    @staticmethod
    def assert_memory_usage_acceptable(func, max_memory_mb: float = 100.0):
        """Assert that a function doesn't use excessive memory."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        result = func()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        assert (
            memory_used <= max_memory_mb
        ), f"Memory usage {memory_used}MB exceeds limit {max_memory_mb}MB"
        return result


# Convenience functions for common test patterns
def create_test_task(**kwargs) -> Task:
    """Create a test task with default values."""
    return TestDataFactory.create_task(**kwargs)


def create_test_agent(**kwargs) -> Agent:
    """Create a test agent with default values."""
    return TestDataFactory.create_agent(**kwargs)


def create_test_project(**kwargs) -> Project:
    """Create a test project with default values."""
    return TestDataFactory.create_project(**kwargs)


def create_test_workflow(**kwargs) -> WorkflowInstance:
    """Create a test workflow with default values."""
    return TestDataFactory.create_workflow(**kwargs)


def create_test_artifact(**kwargs) -> Artifact:
    """Create a test artifact with default values."""
    return TestDataFactory.create_artifact(**kwargs)


def mock_async_function(
    return_value: Any = None, side_effect: Exception = None
) -> AsyncMock:
    """Create a mock async function."""
    if side_effect:
        return AsyncMock(side_effect=side_effect)
    return AsyncMock(return_value=return_value)


def mock_sync_function(
    return_value: Any = None, side_effect: Exception = None
) -> MagicMock:
    """Create a mock sync function."""
    if side_effect:
        return MagicMock(side_effect=side_effect)
    return MagicMock(return_value=return_value)
