import pytest
from uuid import uuid4

from spec_driven_agent.agents.qa_agent import QAAgent
from spec_driven_agent.models.agent import AgentRole
from spec_driven_agent.models.task import Task, TaskStatus


class TestQAAgent:
    @pytest.fixture
    def qa_agent(self):
        return QAAgent(agent_id="qa-001", name="Test QA")

    @pytest.fixture
    def test_plan_task(self):
        return Task(
            task_id="task-qa-001",
            task_name="Create Test Plan",
            task_type="test_plan_generation",
            description="Generate a comprehensive test plan",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=5.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="testing",
        )

    def test_qa_agent_initialization(self, qa_agent):
        assert qa_agent.agent_id == "qa-001"
        assert qa_agent.role == AgentRole.QA
        assert "testing" in qa_agent.capabilities

    @pytest.mark.asyncio
    async def test_qa_agent_process_test_plan(self, qa_agent, test_plan_task):
        result = await qa_agent.process_task(test_plan_task)
        assert result.success is True
        assert "Test plan" in result.message

    @pytest.mark.asyncio
    async def test_qa_agent_generic_task(self, qa_agent):
        generic_task = Task(
            task_id="task-qa-002",
            task_name="Unclassified",
            task_type="random",
            description="A generic QA task",
            status=TaskStatus.PENDING,
            priority="low",
            effort_estimate=2.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="testing",
        )
        result = await qa_agent.process_task(generic_task)
        assert result.success is True
        assert "QA task" in result.message