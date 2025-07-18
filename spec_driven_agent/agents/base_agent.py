"""
Base agent class for the spec-driven workflow system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel

from ..models.agent import AgentCapability, AgentRole
from ..models.context import AgentContext
from ..models.task import Task


class AgentStatus(str, Enum):
    """Agent status enumeration."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class SimpleTaskResult(BaseModel):
    """Simple task result for minimal implementation."""

    task_id: str
    success: bool
    message: Optional[str] = None
    error_message: Optional[str] = None
    artifacts: List[Any] = []


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, agent_id: str, name: str, role: AgentRole):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.status = AgentStatus.IDLE
        self.context: Optional[AgentContext] = None
        self.capabilities: List[AgentCapability] = []

    async def initialize(self, context: Optional[AgentContext] = None) -> None:
        """Initialize the agent with context."""
        self.context = context
        self.status = AgentStatus.IDLE

    async def process_task(self, task: Task) -> SimpleTaskResult:
        """Process a task and return results."""
        try:
            self.status = AgentStatus.BUSY
            result = await self._process_task_impl(task)
            self.status = AgentStatus.IDLE
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            return SimpleTaskResult(
                task_id=task.task_id, success=False, error_message=str(e), artifacts=[]
            )

    @abstractmethod
    async def _process_task_impl(self, task: Task) -> SimpleTaskResult:
        """Implementation of task processing - to be overridden by subclasses."""
        pass

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,  # AgentRole is already a string
            "status": self.status.value,
            "capabilities": self.capabilities,  # capabilities are now strings
        }

    async def ping(self) -> Dict[str, Any]:
        """Ping the agent to check if it's alive."""
        return {
            "agent_id": self.agent_id,
            "status": "alive",
            "timestamp": "2024-01-01T00:00:00Z",
        }
