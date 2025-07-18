from ..models.agent import AgentRole
from ..models.task import Task
from .base_agent import BaseAgent, SimpleTaskResult


class ArchitectAgent(BaseAgent):
    """Architect agent responsible for system design and technology decisions."""

    def __init__(self, agent_id: str = "architect-001", name: str = "Archie Architect"):
        super().__init__(agent_id, name, AgentRole.ARCHITECT)
        # Enumerate the architect's primary skills
        self.capabilities = [
            "system_design",
            "technology_decisions",
            "api_spec_generation",
        ]

    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        """Route the incoming task to the correct architect capability."""
        task_type = task.task_type.lower()

        if "design" in task_type or "architecture" in task_type:
            return await self._design_system(task)
        elif "technology" in task_type or "tech_decision" in task_type:
            return await self._make_technology_decision(task)
        elif "api" in task_type and ("spec" in task_type or "definition" in task_type):
            return await self._generate_api_spec(task)
        else:
            return await self._generic_architecture_task(task)

    # ----- Capability Implementations --------------------------------------------------
    async def _design_system(self, task: Task) -> SimpleTaskResult:
        """Perform high-level system design."""
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="System design completed successfully",
            artifacts=[],
        )

    async def _make_technology_decision(self, task: Task) -> SimpleTaskResult:
        """Choose technology stack or make specific technology decisions."""
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Technology decisions documented successfully",
            artifacts=[],
        )

    async def _generate_api_spec(self, task: Task) -> SimpleTaskResult:
        """Generate an API specification."""
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="API specification generated successfully",
            artifacts=[],
        )

    async def _generic_architecture_task(self, task: Task) -> SimpleTaskResult:
        """Fallback for unclassified architect tasks."""
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Architecture task completed successfully",
            artifacts=[],
        )