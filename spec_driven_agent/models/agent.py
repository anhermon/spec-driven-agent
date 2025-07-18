"""
Agent models for the spec-driven agent workflow system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class AgentRole(str):
    """Agent role enumeration."""

    ANALYST = "analyst"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    SCRUM_MASTER = "scrum_master"
    DEVELOPER = "developer"
    QA = "qa"
    UX_EXPERT = "ux_expert"
    PRODUCT_OWNER = "product_owner"


class AgentCapability(StatusModel):
    """Represents a capability of an agent."""

    capability_id: str = Field(..., description="Unique capability identifier")
    capability_name: str = Field(..., description="Human-readable capability name")
    capability_type: str = Field(..., description="Type of capability")

    # Capability details
    description: str = Field(..., description="Capability description")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Capability parameters"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Capability constraints"
    )

    # Performance metrics
    success_rate: Optional[float] = Field(None, description="Success rate percentage")
    average_execution_time: Optional[float] = Field(
        None, description="Average execution time in seconds"
    )
    execution_count: int = Field(default=0, description="Number of executions")

    # Status
    enabled: bool = Field(default=True, description="Whether capability is enabled")
    version: str = Field(default="1.0.0", description="Capability version")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class AgentContext(StatusModel):
    """Represents the context for an agent."""

    agent_id: UUID = Field(..., description="Associated agent ID")
    context_type: str = Field(default="agent_context", description="Context type")

    # Context data
    current_task: Optional[str] = Field(
        None, description="Current task being worked on"
    )
    task_history: List[str] = Field(default_factory=list, description="Task history")
    knowledge_base: Dict[str, Any] = Field(
        default_factory=dict, description="Agent knowledge base"
    )

    # Communication
    recent_messages: List[str] = Field(
        default_factory=list, description="Recent message IDs"
    )
    communication_history: List[str] = Field(
        default_factory=list, description="Communication history"
    )

    # State
    current_state: str = Field(default="idle", description="Current agent state")
    state_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="State history"
    )

    # Performance
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow, description="Last activity timestamp"
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class AgentMessage(StatusModel):
    """Represents a message between agents."""

    message_id: str = Field(..., description="Unique message identifier")
    sender_id: UUID = Field(..., description="Sender agent ID")
    recipient_id: Optional[UUID] = Field(None, description="Recipient agent ID")

    # Message content
    message_type: str = Field(..., description="Type of message")
    content: Dict[str, Any] = Field(..., description="Message content")
    priority: str = Field(default="normal", description="Message priority")

    # Metadata
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )
    expires_at: Optional[datetime] = Field(None, description="Message expiration time")

    # Status
    delivered: bool = Field(default=False, description="Whether message was delivered")
    read: bool = Field(default=False, description="Whether message was read")
    processed: bool = Field(default=False, description="Whether message was processed")

    # Routing
    routing_path: List[UUID] = Field(
        default_factory=list, description="Message routing path"
    )
    retry_count: int = Field(default=0, description="Number of retry attempts")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class Agent(StatusModel):
    """Represents an AI agent in the spec-driven workflow."""

    # Agent identification
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent")
    agent_name: str = Field(..., description="Human-readable agent name")

    # Role and capabilities
    role: AgentRole = Field(..., description="Agent role")
    capabilities: List[AgentCapability] = Field(
        default_factory=list, description="Agent capabilities"
    )
    specializations: List[str] = Field(
        default_factory=list, description="Agent specializations"
    )

    # Configuration
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Agent configuration"
    )
    settings: Dict[str, Any] = Field(default_factory=dict, description="Agent settings")

    # Context and state
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    current_workflow_id: Optional[UUID] = Field(None, description="Current workflow ID")
    current_task_id: Optional[UUID] = Field(None, description="Current task ID")

    # Communication
    communication_protocol: str = Field(
        default="a2a", description="Communication protocol"
    )
    endpoint_url: Optional[str] = Field(None, description="Agent endpoint URL")
    api_key: Optional[str] = Field(None, description="Agent API key")

    # Performance and metrics
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )
    task_completion_rate: Optional[float] = Field(
        None, description="Task completion rate"
    )
    average_response_time: Optional[float] = Field(
        None, description="Average response time"
    )

    # Status and availability
    status: str = Field(default="available", description="Agent status")
    availability: str = Field(default="available", description="Agent availability")
    last_heartbeat: Optional[datetime] = Field(
        None, description="Last heartbeat timestamp"
    )

    # Workload
    current_workload: int = Field(default=0, description="Current workload")
    max_workload: int = Field(default=10, description="Maximum workload capacity")
    queue_length: int = Field(default=0, description="Task queue length")

    # Relationships
    supervisor_id: Optional[UUID] = Field(None, description="Supervisor agent ID")
    subordinate_ids: List[UUID] = Field(
        default_factory=list, description="Subordinate agent IDs"
    )
    collaborator_ids: List[UUID] = Field(
        default_factory=list, description="Collaborator agent IDs"
    )

    # History
    task_history: List[UUID] = Field(default_factory=list, description="Task history")
    workflow_history: List[UUID] = Field(
        default_factory=list, description="Workflow history"
    )
    message_history: List[str] = Field(
        default_factory=list, description="Message history"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
