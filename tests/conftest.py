"""
Pytest configuration and shared fixtures for spec-driven-agent tests.

This module is imported by Pytest *before* any test modules are collected.
Here we apply a small monkey-patch that makes Pydantic v1 work on Python 3.13
by adapting the changed private ``typing.ForwardRef._evaluate`` signature.
The patch is completely self-contained and safe to apply multiple times.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Compatibility shim – Pydantic v1 vs Python 3.13
# ---------------------------------------------------------------------------
# Python 3.13 added a new required ``recursive_guard`` kw-only argument to
# ``typing.ForwardRef._evaluate``.  Older versions of Pydantic (<=1.10) still
# invoke this private method with the legacy positional signature which now
# raises ``TypeError`` at import time (e.g. when FastAPI defines its OpenAPI
# models).  We solve this once for the entire test session by wrapping the
# method and injecting the missing argument when absent.

import typing as _typing


_orig_fr_evaluate = _typing.ForwardRef._evaluate  # type: ignore[attr-defined]


def _forwardref_eval_shim(self: _typing.ForwardRef, globalns, localns, *args, **kwargs):  # type: ignore[override]
    if "recursive_guard" not in kwargs:
        kwargs["recursive_guard"] = set()
    return _orig_fr_evaluate(self, globalns, localns, *args, **kwargs)


_typing.ForwardRef._evaluate = _forwardref_eval_shim  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Fixtures (existing content continues below)
# ---------------------------------------------------------------------------

import asyncio
from typing import Any, Dict, List
from uuid import uuid4

import pytest

from spec_driven_agent.agents.agent_manager import AgentManager
from spec_driven_agent.agents.analyst_agent import AnalystAgent
from spec_driven_agent.agents.base_agent import BaseAgent
from spec_driven_agent.agents.product_manager_agent import ProductManagerAgent
from spec_driven_agent.models.agent import Agent, AgentRole
from spec_driven_agent.models.artifact import Artifact, ArtifactType
from spec_driven_agent.models.context import ContextUpdate, SpecDrivenContext
from spec_driven_agent.models.project import Project, ProjectStatus
from spec_driven_agent.models.task import Task, TaskStatus
from spec_driven_agent.models.workflow import (
    WorkflowInstance,
    WorkflowPhase,
    WorkflowStatus,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_agent_data() -> Dict[str, Any]:
    """Sample agent data for testing."""
    return {
        "id": str(uuid4()),
        "name": "Test Agent",
        "agent_type": "analyst",
        "status": "active",
        "capabilities": ["requirements_gathering", "market_research"],
        "description": "A test agent for unit testing",
        "version": "1.0.0",
    }


@pytest.fixture
def sample_task_data() -> Dict[str, Any]:
    """Sample task data for testing."""
    return {
        "id": str(uuid4()),
        "name": "Test Task",
        "description": "A test task for unit testing",
        "task_type": "requirements_gathering",
        "status": TaskStatus.PENDING,
        "priority": "medium",
        "estimated_hours": 4.0,
        "assigned_agent_id": None,
        "project_id": str(uuid4()),
        "workflow_id": str(uuid4()),
        "context": {"test": "data"},
    }


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "slug": "test-project",
        "description": "A test project for unit testing",
        "current_phase": ProjectStatus.DRAFT,
        "stakeholders": [],
        "tags": ["test", "unit-testing"],
    }


@pytest.fixture
def sample_context_data() -> Dict[str, Any]:
    """Sample context data for testing."""
    return {
        "project_id": uuid4(),
        "context_type": "spec_driven",
        "requirements": {"functional": [], "non_functional": []},
        "specifications": {},
        "architecture": {},
        "implementation": {},
        "symbolic_data": {},
        "symbolic_references": {},
    }


@pytest.fixture
def sample_workflow_data() -> Dict[str, Any]:
    """Sample workflow data for testing."""
    return {
        "project_id": uuid4(),
        "workflow_type": "spec_driven",
        "current_phase": WorkflowPhase.DISCOVERY,
        "completed_phases": [],
        "assigned_agents": [],
        "task_queue": [],
        "completed_tasks": [],
    }


@pytest.fixture
def sample_artifact_data() -> Dict[str, Any]:
    """Sample artifact data for testing."""
    return {
        "artifact_id": str(uuid4()),
        "artifact_name": "Test Artifact",
        "artifact_type": ArtifactType.DOCUMENT,
        "content": "Test content",
        "description": "A test artifact",
        "project_id": uuid4(),
        "phase": "discovery",
    }


@pytest.fixture
def sample_agent() -> Agent:
    """Create a sample agent instance."""
    return Agent(
        agent_id=str(uuid4()),
        agent_name="Test Agent",
        agent_type="analyst",
        role=AgentRole.ANALYST,
        status="active",
        capabilities=[],
        config={},
        settings={},
    )


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task instance."""
    return Task(
        task_id=str(uuid4()),
        task_name="Test Task",
        description="A test task for unit testing",
        task_type="requirements_gathering",
        status=TaskStatus.PENDING,
        priority="medium",
        effort_estimate=4.0,
        assigned_agent_id=None,
        workflow_id=uuid4(),
        phase="discovery",
    )


@pytest.fixture
def sample_project() -> Project:
    """Create a sample project instance."""
    return Project(
        name="Test Project",
        slug="test-project",
        description="A test project for unit testing",
        current_phase=ProjectStatus.DRAFT,
        stakeholders=[],
        tags=["test", "unit-testing"],
    )


@pytest.fixture
def sample_context() -> SpecDrivenContext:
    """Create a sample context instance."""
    return SpecDrivenContext(
        project_id=uuid4(),
        context_type="spec_driven",
        requirements={"functional": [], "non_functional": []},
        specifications={},
        architecture={},
        implementation={},
        symbolic_data={},
        symbolic_references={},
    )


@pytest.fixture
def sample_workflow() -> WorkflowInstance:
    """Create a sample workflow instance."""
    return WorkflowInstance(
        project_id=uuid4(),
        workflow_type="spec_driven",
        current_phase=WorkflowPhase.DISCOVERY,
        completed_phases=[],
        assigned_agents=[],
        task_queue=[],
        completed_tasks=[],
    )


@pytest.fixture
def sample_artifact() -> Artifact:
    """Create a sample artifact instance."""
    return Artifact(
        artifact_id=str(uuid4()),
        artifact_name="Test Artifact",
        artifact_type=ArtifactType.DOCUMENT,
        content="Test content",
        description="A test artifact",
        project_id=uuid4(),
        phase="discovery",
    )


@pytest.fixture
def agent_manager() -> AgentManager:
    """Create an agent manager instance for testing."""
    return AgentManager()


@pytest.fixture
def analyst_agent() -> AnalystAgent:
    """Create an analyst agent instance for testing."""
    return AnalystAgent(
        agent_id="analyst-001",
        name="Test Analyst",
        description="A test analyst agent",
    )


@pytest.fixture
def product_manager_agent() -> ProductManagerAgent:
    """Create a product manager agent instance for testing."""
    return ProductManagerAgent(
        agent_id="pm-001",
        name="Test Product Manager",
        description="A test product manager agent",
    )


@pytest.fixture
def mock_task_result() -> Dict[str, Any]:
    """Mock task result for testing."""
    return {
        "task_id": str(uuid4()),
        "status": "completed",
        "result": {
            "summary": "Task completed successfully",
            "artifacts": [],
            "metrics": {"quality_score": 0.9},
        },
        "artifacts": [],
        "metadata": {"test": True},
    }


@pytest.fixture
def sample_context_update() -> ContextUpdate:
    """Create a sample context update for testing."""
    return ContextUpdate(
        id=uuid4(),
        name="Test Update",
        description="A test context update",
        status="pending",
        context_id=str(uuid4()),
        update_type="requirements",
        update_data={"new_requirement": "Test requirement"},
        source_type="test",
    )


@pytest.fixture
def multiple_agents() -> List[Agent]:
    """Create multiple agents for testing."""
    return [
        Agent(
            agent_id="analyst-001",
            agent_name="Analyst Agent",
            agent_type="analyst",
            role=AgentRole.ANALYST,
            status="active",
            capabilities=[],
            config={},
            settings={},
        ),
        Agent(
            agent_id="pm-001",
            agent_name="Product Manager Agent",
            agent_type="project_manager",
            role=AgentRole.PROJECT_MANAGER,
            status="active",
            capabilities=[],
            config={},
            settings={},
        ),
    ]


@pytest.fixture
def multiple_tasks() -> List[Task]:
    """Create multiple tasks for testing."""
    return [
        Task(
            task_id="task-001",
            task_name="Requirements Gathering",
            description="Gather project requirements",
            task_type="requirements_gathering",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=8.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        ),
        Task(
            task_id="task-002",
            task_name="Create PRD",
            description="Create product requirements document",
            task_type="prd_creation",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=12.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="planning",
        ),
    ]
