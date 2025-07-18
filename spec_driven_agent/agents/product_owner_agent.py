from ..models.agent import AgentRole
from ..models.task import Task
from .base_agent import BaseAgent, SimpleTaskResult


class ProductOwnerAgent(BaseAgent):
    """Product Owner agent responsible for acceptance and stakeholder communication."""

    def __init__(self, agent_id: str = "po-001", name: str = "Paula Product Owner"):
        super().__init__(agent_id, name, AgentRole.PRODUCT_OWNER)
        self.capabilities = [
            "final_validation",
            "acceptance",
            "stakeholder_communication",
        ]

    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        task_type = task.task_type.lower()

        if "validate" in task_type or "validation" in task_type:
            return await self._validate_delivery(task)
        elif "accept" in task_type or "acceptance" in task_type:
            return await self._accept_feature(task)
        elif "communicate" in task_type or "stakeholder" in task_type:
            return await self._communicate_with_stakeholders(task)
        else:
            return await self._generic_po_task(task)

    # ----- Capability Implementations --------------------------------------------------
    async def _validate_delivery(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Delivery validated successfully",
            artifacts=[],
        )

    async def _accept_feature(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Feature accepted successfully",
            artifacts=[],
        )

    async def _communicate_with_stakeholders(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Stakeholders communicated with successfully",
            artifacts=[],
        )

    async def _generic_po_task(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Product owner task completed successfully",
            artifacts=[],
        )