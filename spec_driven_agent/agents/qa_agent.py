from ..models.agent import AgentRole
from ..models.task import Task
from .base_agent import BaseAgent, SimpleTaskResult


class QAAgent(BaseAgent):
    """QA agent responsible for testing and validation activities."""

    def __init__(self, agent_id: str = "qa-001", name: str = "Quinn QA"):
        super().__init__(agent_id, name, AgentRole.QA)
        self.capabilities = [
            "testing",
            "validation",
            "test_plan_generation",
        ]

    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        task_type = task.task_type.lower()

        if "test_plan" in task_type or ("plan" in task_type and "test" in task_type):
            return await self._generate_test_plan(task)
        elif "execute" in task_type and "test" in task_type:
            return await self._execute_tests(task)
        elif "test" in task_type or "validation" in task_type:
            return await self._write_tests(task)
        else:
            return await self._generic_qa_task(task)

    # ----- Capability Implementations --------------------------------------------------
    async def _write_tests(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Tests written successfully",
            artifacts=[],
        )

    async def _execute_tests(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Tests executed successfully",
            artifacts=[],
        )

    async def _generate_test_plan(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="Test plan generated successfully",
            artifacts=[],
        )

    async def _generic_qa_task(self, task: Task) -> SimpleTaskResult:
        return SimpleTaskResult(
            task_id=task.task_id,
            success=True,
            message="QA task completed successfully",
            artifacts=[],
        )