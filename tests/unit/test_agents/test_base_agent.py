"""
Unit tests for BaseAgent functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from spec_driven_agent.agents.base_agent import BaseAgent, SimpleTaskResult
from spec_driven_agent.models.task import Task, TaskStatus
from spec_driven_agent.models.agent import Agent, AgentRole


class TestAgent(BaseAgent):
    """Concrete test agent for testing BaseAgent functionality."""
    
    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        """Test implementation of task processing."""
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Test task completed",
            artifacts=[]
        )


class TestBaseAgent:
    """Test BaseAgent functionality."""

    @pytest.fixture
    def base_agent(self):
        """Create a base agent instance for testing."""
        return TestAgent(
            agent_id="test-agent-001",
            name="Test Base Agent",
            role=AgentRole.ANALYST,
        )

    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return Task(
            task_id="task-001",
            task_name="Test Task",
            task_type="requirements_gathering",
            description="A test task",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )

    def test_base_agent_initialization(self, base_agent):
        """Test base agent initialization."""
        assert base_agent.agent_id == "test-agent-001"
        assert base_agent.name == "Test Base Agent"
        assert base_agent.role == AgentRole.ANALYST
        assert base_agent.status.value == "idle"
        assert base_agent.capabilities == []

    @pytest.mark.asyncio
    async def test_base_agent_process_task_success(self, base_agent, sample_task):
        """Test successful task processing."""
        result = await base_agent.process_task(sample_task)
        
        assert result.task_id == "task-001"
        assert result.success is True
        assert result.message == "Test task completed"
        assert result.artifacts == []

    @pytest.mark.asyncio
    async def test_base_agent_process_task_failure(self, base_agent, sample_task):
        """Test task processing failure."""
        # Mock the process_task_implementation method to raise an exception
        base_agent._process_task_impl = AsyncMock(
            side_effect=Exception("Task processing failed")
        )
        
        result = await base_agent.process_task(sample_task)
        
        assert result.task_id == "task-001"
        assert result.success is False
        assert "Task processing failed" in result.error_message

    @pytest.mark.asyncio
    async def test_base_agent_get_status(self, base_agent):
        """Test agent status retrieval."""
        status = await base_agent.get_status()
        
        assert status["agent_id"] == "test-agent-001"
        assert status["name"] == "Test Base Agent"
        assert status["role"] == "analyst"
        assert status["status"] == "idle"
        assert status["capabilities"] == []

    @pytest.mark.asyncio
    async def test_base_agent_ping(self, base_agent):
        """Test agent ping functionality."""
        response = await base_agent.ping()
        
        assert response["agent_id"] == "test-agent-001"
        assert response["status"] == "alive"
        assert "timestamp" in response

    def test_base_agent_str_representation(self, base_agent):
        """Test string representation of agent."""
        str_repr = str(base_agent)
        assert "Test Base Agent" in str_repr
        assert "test-agent-001" in str_repr

    def test_base_agent_repr_representation(self, base_agent):
        """Test repr representation of agent."""
        repr_str = repr(base_agent)
        assert "TestAgent" in repr_str
        assert "test-agent-001" in repr_str

    def test_base_agent_equality(self, base_agent):
        """Test agent equality comparison."""
        agent1 = TestAgent(
            agent_id="test-agent-001",
            name="Test Base Agent",
            role=AgentRole.ANALYST,
        )
        agent2 = TestAgent(
            agent_id="test-agent-001",
            name="Test Base Agent",
            role=AgentRole.ANALYST,
        )
        agent3 = TestAgent(
            agent_id="different-agent",
            name="Different Agent",
            role=AgentRole.PRODUCT_MANAGER,
        )
        
        assert agent1.agent_id == agent2.agent_id
        assert agent1.agent_id != agent3.agent_id 