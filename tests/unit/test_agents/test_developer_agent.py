import pytest
from uuid import uuid4

from spec_driven_agent.agents.developer_agent import DeveloperAgent
from spec_driven_agent.models.agent import AgentRole
from spec_driven_agent.models.task import Task, TaskStatus


class TestDeveloperAgent:
    """Tests for DeveloperAgent functionality."""

    @pytest.fixture
    def developer_agent(self):
        return DeveloperAgent(agent_id="dev-001", name="Test Developer")

    @pytest.fixture
    def code_task(self):
        return Task(
            task_id="task-dev-001",
            task_name="Generate Code",
            task_type="code_generation",
            description="Generate source code for feature X",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=12.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="development",
        )

    def test_developer_agent_initialization(self, developer_agent):
        assert developer_agent.agent_id == "dev-001"
        assert developer_agent.role == AgentRole.DEVELOPER
        assert "code_generation" in developer_agent.capabilities

    @pytest.mark.asyncio
    async def test_developer_agent_process_code_task(self, developer_agent, code_task):
        result = await developer_agent.process_task(code_task)
        assert result.success is True
        assert "Code generated" in result.message

    @pytest.mark.asyncio
    async def test_developer_agent_generic_task(self, developer_agent):
        generic_task = Task(
            task_id="task-dev-002",
            task_name="Unclassified",
            task_type="maintenance",
            description="A generic dev task",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=3.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="development",
        )
        result = await developer_agent.process_task(generic_task)
        assert result.success is True
        assert "Development task" in result.message