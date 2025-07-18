import pytest
from uuid import uuid4

from spec_driven_agent.agents.product_owner_agent import ProductOwnerAgent
from spec_driven_agent.models.agent import AgentRole
from spec_driven_agent.models.task import Task, TaskStatus


class TestProductOwnerAgent:
    @pytest.fixture
    def po_agent(self):
        return ProductOwnerAgent(agent_id="po-001", name="Test PO")

    @pytest.fixture
    def validation_task(self):
        return Task(
            task_id="task-po-001",
            task_name="Validate Delivery",
            task_type="final_validation",
            description="Validate final delivery",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="acceptance",
        )

    def test_po_agent_initialization(self, po_agent):
        assert po_agent.agent_id == "po-001"
        assert po_agent.role == AgentRole.PRODUCT_OWNER
        assert "final_validation" in po_agent.capabilities

    @pytest.mark.asyncio
    async def test_po_agent_process_validation(self, po_agent, validation_task):
        result = await po_agent.process_task(validation_task)
        assert result.success is True
        assert "validated" in result.message

    @pytest.mark.asyncio
    async def test_po_agent_generic_task(self, po_agent):
        generic_task = Task(
            task_id="task-po-002",
            task_name="Unclassified",
            task_type="other",
            description="Generic PO task",
            status=TaskStatus.PENDING,
            priority="low",
            effort_estimate=2.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="acceptance",
        )
        result = await po_agent.process_task(generic_task)
        assert result.success is True
        assert "Product owner task" in result.message