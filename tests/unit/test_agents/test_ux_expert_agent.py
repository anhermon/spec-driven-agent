import pytest
from uuid import uuid4

from spec_driven_agent.agents.ux_expert_agent import UXExpertAgent
from spec_driven_agent.models.agent import AgentRole
from spec_driven_agent.models.task import Task, TaskStatus


class TestUXExpertAgent:
    @pytest.fixture
    def ux_agent(self):
        return UXExpertAgent(agent_id="ux-001", name="Test UX Expert")

    @pytest.fixture
    def wireframe_task(self):
        return Task(
            task_id="task-ux-001",
            task_name="Create Wireframe",
            task_type="wireframe_generation",
            description="Generate wireframes for new UI",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=5.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="design",
        )

    def test_ux_agent_initialization(self, ux_agent):
        assert ux_agent.agent_id == "ux-001"
        assert ux_agent.role == AgentRole.UX_EXPERT
        assert "wireframe_generation" in ux_agent.capabilities

    @pytest.mark.asyncio
    async def test_ux_agent_process_wireframe(self, ux_agent, wireframe_task):
        result = await ux_agent.process_task(wireframe_task)
        assert result.success is True
        assert "Wireframe" in result.message

    @pytest.mark.asyncio
    async def test_ux_agent_generic_task(self, ux_agent):
        generic_task = Task(
            task_id="task-ux-002",
            task_name="Unclassified",
            task_type="random",
            description="A generic UX task",
            status=TaskStatus.PENDING,
            priority="low",
            effort_estimate=2.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="design",
        )
        result = await ux_agent.process_task(generic_task)
        assert result.success is True
        assert "UX task" in result.message