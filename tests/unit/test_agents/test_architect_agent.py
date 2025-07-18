import pytest
from uuid import uuid4

from spec_driven_agent.agents.architect_agent import ArchitectAgent
from spec_driven_agent.models.agent import AgentRole
from spec_driven_agent.models.task import Task, TaskStatus


class TestArchitectAgent:
    """Tests for ArchitectAgent functionality."""

    @pytest.fixture
    def architect_agent(self):
        return ArchitectAgent(agent_id="architect-001", name="Test Architect")

    @pytest.fixture
    def design_task(self):
        return Task(
            task_id="task-arch-001",
            task_name="System Design",
            task_type="system_design",
            description="Design the overall system architecture",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=10.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="architecture",
        )

    @pytest.fixture
    def api_spec_task(self):
        return Task(
            task_id="task-arch-002",
            task_name="API Spec Generation",
            task_type="api_spec_generation",
            description="Generate API specifications",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=6.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="architecture",
        )

    def test_architect_agent_initialization(self, architect_agent):
        assert architect_agent.agent_id == "architect-001"
        assert architect_agent.role == AgentRole.ARCHITECT
        assert "system_design" in architect_agent.capabilities
        assert "api_spec_generation" in architect_agent.capabilities

    @pytest.mark.asyncio
    async def test_architect_agent_process_design_task(self, architect_agent, design_task):
        result = await architect_agent.process_task(design_task)
        assert result.success is True
        assert "System design" in result.message

    @pytest.mark.asyncio
    async def test_architect_agent_process_api_spec_task(self, architect_agent, api_spec_task):
        result = await architect_agent.process_task(api_spec_task)
        assert result.success is True
        assert "API specification" in result.message

    @pytest.mark.asyncio
    async def test_architect_agent_generic_task(self, architect_agent):
        generic_task = Task(
            task_id="task-arch-003",
            task_name="Unclassified",
            task_type="random_task",
            description="A generic architecture task",
            status=TaskStatus.PENDING,
            priority="low",
            effort_estimate=2.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="architecture",
        )
        result = await architect_agent.process_task(generic_task)
        assert result.success is True
        assert "Architecture task" in result.message