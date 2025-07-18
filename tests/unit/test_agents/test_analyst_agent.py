"""
Unit tests for AnalystAgent functionality.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from spec_driven_agent.agents.analyst_agent import AnalystAgent
from spec_driven_agent.models.agent import Agent, AgentRole
from spec_driven_agent.models.task import Task, TaskStatus


class TestAnalystAgent:
    """Test AnalystAgent functionality."""

    @pytest.fixture
    def analyst_agent(self):
        """Create an analyst agent instance for testing."""
        return AnalystAgent(
            agent_id="analyst-001",
            name="Test Analyst",
        )

    @pytest.fixture
    def requirements_task(self):
        """Create a requirements gathering task."""
        return Task(
            task_id="task-001",
            task_name="Requirements Gathering",
            task_type="requirements_gathering",
            description="Gather project requirements",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=8.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )

    @pytest.fixture
    def market_research_task(self):
        """Create a market research task."""
        return Task(
            task_id="task-002",
            task_name="Market Research",
            task_type="market_research",
            description="Conduct market research",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=6.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )

    def test_analyst_agent_initialization(self, analyst_agent):
        """Test analyst agent initialization."""
        assert analyst_agent.agent_id == "analyst-001"
        assert analyst_agent.name == "Test Analyst"
        assert analyst_agent.role == AgentRole.ANALYST
        assert "requirements_gathering" in analyst_agent.capabilities
        assert "market_research" in analyst_agent.capabilities
        assert "stakeholder_interviews" in analyst_agent.capabilities

    @pytest.mark.asyncio
    async def test_analyst_agent_process_requirements_task(
        self, analyst_agent, requirements_task
    ):
        """Test processing requirements gathering task."""
        result = await analyst_agent.process_task(requirements_task)

        assert result.task_id == "task-001"
        assert result.success is True
        assert "Requirements gathered" in result.message

    @pytest.mark.asyncio
    async def test_analyst_agent_process_market_research_task(
        self, analyst_agent, market_research_task
    ):
        """Test processing market research task."""
        result = await analyst_agent.process_task(market_research_task)

        assert result.task_id == "task-002"
        assert result.success is True
        assert "Market research" in result.message

    @pytest.mark.asyncio
    async def test_analyst_agent_process_unsupported_task(self, analyst_agent):
        """Test processing unsupported task type."""
        unsupported_task = Task(
            task_id="task-003",
            task_name="Unsupported Task",
            task_type="prd_creation",  # Not supported by analyst
            description="An unsupported task type",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="planning",
        )

        result = await analyst_agent.process_task(unsupported_task)

        assert result.task_id == "task-003"
        assert result.success is True  # Generic analysis handles unsupported tasks
        assert "Analysis completed" in result.message

    @pytest.mark.asyncio
    async def test_analyst_agent_gather_requirements(
        self, analyst_agent, requirements_task
    ):
        """Test requirements gathering functionality."""
        result = await analyst_agent._gather_requirements(requirements_task)

        assert result.task_id == "task-001"
        assert result.success is True
        assert "Requirements gathered" in result.message

    @pytest.mark.asyncio
    async def test_analyst_agent_conduct_market_research(
        self, analyst_agent, market_research_task
    ):
        """Test market research functionality."""
        result = await analyst_agent._conduct_market_research(market_research_task)

        assert result.task_id == "task-002"
        assert result.success is True
        assert "Market research" in result.message

    @pytest.mark.asyncio
    async def test_analyst_agent_conduct_stakeholder_interviews(self, analyst_agent):
        """Test stakeholder interview functionality."""
        interview_task = Task(
            task_id="task-004",
            task_name="Stakeholder Interviews",
            task_type="stakeholder_interviews",
            description="Conduct stakeholder interviews",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )

        result = await analyst_agent._conduct_interview(interview_task)

        assert result.task_id == "task-004"
        assert result.success is True
        assert "Stakeholder interviews" in result.message

    def test_analyst_agent_str_representation(self, analyst_agent):
        """Test string representation of analyst agent."""
        str_repr = str(analyst_agent)
        assert "Test Analyst" in str_repr
        assert "analyst-001" in str_repr

    def test_analyst_agent_repr_representation(self, analyst_agent):
        """Test repr representation of analyst agent."""
        repr_str = repr(analyst_agent)
        assert "AnalystAgent" in repr_str
        assert "analyst-001" in repr_str

    @pytest.mark.asyncio
    async def test_analyst_agent_task_with_empty_context(self, analyst_agent):
        """Test processing task with empty context."""
        empty_context_task = Task(
            task_id="task-006",
            task_name="Empty Context Task",
            task_type="requirements_gathering",
            description="A task with empty context",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )

        result = await analyst_agent.process_task(empty_context_task)

        assert result.task_id == "task-006"
        assert result.success is True
        assert "Requirements gathered" in result.message

    @pytest.mark.asyncio
    async def test_analyst_agent_task_with_complex_context(self, analyst_agent):
        """Test processing task with complex context."""
        complex_context_task = Task(
            task_id="task-007",
            task_name="Complex Context Task",
            task_type="requirements_gathering",
            description="A task with complex context",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=8.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )

        result = await analyst_agent.process_task(complex_context_task)

        assert result.task_id == "task-007"
        assert result.success is True
        assert "Requirements gathered" in result.message
