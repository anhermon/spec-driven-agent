from ..models.agent import AgentRole
from ..models.task import Task
from .base_agent import BaseAgent, SimpleTaskResult


class DeveloperAgent(BaseAgent):
    """Developer agent responsible for code implementation and feature development."""

    def __init__(self, agent_id: str = "dev-001", name: str = "Devon Developer"):
        super().__init__(agent_id, name, AgentRole.DEVELOPER)
        self.capabilities = [
            "code_generation",
            "implementation",
            "user_story_processing",
        ]

    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        task_type = task.task_type.lower()

        if "code" in task_type or "implementation" in task_type or "implement" in task_type:
            return await self._generate_code(task)
        elif "feature" in task_type:
            return await self._implement_feature(task)
        elif "story" in task_type or "user_story" in task_type:
            return await self._process_user_story(task)
        else:
            return await self._generic_development_task(task)

    # ----- Capability Implementations --------------------------------------------------
    async def _generate_code(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Code generated successfully",
            artifacts=[],
        )

    async def _implement_feature(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Feature implemented successfully",
            artifacts=[],
        )

    async def _process_user_story(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="User story processed successfully",
            artifacts=[],
        )

    async def _generic_development_task(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Development task completed successfully",
            artifacts=[],
        )