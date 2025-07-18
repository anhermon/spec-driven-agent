from ..models.agent import AgentRole
from ..models.task import Task
from .base_agent import BaseAgent, SimpleTaskResult


class UXExpertAgent(BaseAgent):
    """UX Expert agent responsible for user experience design and mockups."""

    def __init__(self, agent_id: str = "ux-001", name: str = "Uma UX"):
        super().__init__(agent_id, name, AgentRole.UX_EXPERT)
        self.capabilities = [
            "ux_design",
            "wireframe_generation",
            "mockup_generation",
        ]

    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        task_type = task.task_type.lower()

        if "wireframe" in task_type:
            return await self._create_wireframe(task)
        elif "mockup" in task_type:
            return await self._create_mockup(task)
        elif "ux" in task_type or "design" in task_type:
            return await self._design_experience(task)
        else:
            return await self._generic_ux_task(task)

    # ----- Capability Implementations --------------------------------------------------
    async def _design_experience(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="User experience designed successfully",
            artifacts=[],
        )

    async def _create_wireframe(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Wireframe created successfully",
            artifacts=[],
        )

    async def _create_mockup(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Mockup created successfully",
            artifacts=[],
        )

    async def _generic_ux_task(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="UX task completed successfully",
            artifacts=[],
        )