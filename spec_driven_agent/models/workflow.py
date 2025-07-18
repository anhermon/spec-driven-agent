"""
Workflow models for the spec-driven agent workflow system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class WorkflowPhase(str):
    """Workflow phase enumeration."""
    
    DISCOVERY = "discovery"
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


class WorkflowStatus(str):
    """Workflow status enumeration."""
    
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(StatusModel):
    """Represents the current state of a workflow."""
    
    workflow_id: UUID = Field(..., description="Associated workflow ID")
    current_phase: WorkflowPhase = Field(..., description="Current workflow phase")
    phase_started_at: datetime = Field(default_factory=datetime.utcnow, description="When current phase started")
    phase_completed_at: Optional[datetime] = Field(None, description="When current phase completed")
    
    # Phase-specific data
    phase_data: Dict[str, Any] = Field(default_factory=dict, description="Phase-specific data and artifacts")
    
    # Agent assignments
    active_agents: List[UUID] = Field(default_factory=list, description="Currently active agent IDs")
    completed_agents: List[UUID] = Field(default_factory=list, description="Completed agent IDs")
    
    # Task tracking
    pending_tasks: List[UUID] = Field(default_factory=list, description="Pending task IDs")
    active_tasks: List[UUID] = Field(default_factory=list, description="Active task IDs")
    completed_tasks: List[UUID] = Field(default_factory=list, description="Completed task IDs")
    
    # Dependencies
    satisfied_dependencies: List[str] = Field(default_factory=list, description="Satisfied dependency IDs")
    pending_dependencies: List[str] = Field(default_factory=list, description="Pending dependency IDs")
    
    # User interactions
    user_approvals: List[str] = Field(default_factory=list, description="User approval checkpoints")
    pending_decisions: List[str] = Field(default_factory=list, description="Pending user decisions")
    
    class Config:
        """Pydantic configuration."""
        
        use_enum_values = True
        validate_assignment = True


class WorkflowInstance(StatusModel):
    """Represents a workflow instance for a project."""
    
    # Workflow identification
    project_id: UUID = Field(..., description="Associated project ID")
    workflow_type: str = Field(default="spec_driven", description="Type of workflow")
    
    # Phase management
    current_phase: WorkflowPhase = Field(default=WorkflowPhase.DISCOVERY, description="Current workflow phase")
    completed_phases: List[WorkflowPhase] = Field(default_factory=list, description="Completed phases")
    phase_history: List[Dict[str, Any]] = Field(default_factory=list, description="Phase transition history")
    
    # State management
    state_id: Optional[UUID] = Field(None, description="Current state ID")
    state_history: List[UUID] = Field(default_factory=list, description="State history IDs")
    
    # Agent coordination
    assigned_agents: List[UUID] = Field(default_factory=list, description="Assigned agent IDs")
    agent_roles: Dict[UUID, str] = Field(default_factory=dict, description="Agent role assignments")
    
    # Task management
    task_queue: List[UUID] = Field(default_factory=list, description="Task queue")
    completed_tasks: List[UUID] = Field(default_factory=list, description="Completed tasks")
    
    # Context and artifacts
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    artifact_ids: List[UUID] = Field(default_factory=list, description="Generated artifact IDs")
    
    # Timeline
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Workflow start time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    actual_completion: Optional[datetime] = Field(None, description="Actual completion time")
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Workflow settings")
    
    class Config:
        """Pydantic configuration."""
        
        use_enum_values = True
        validate_assignment = True


class WorkflowTransition(StatusModel):
    """Represents a workflow phase transition."""
    
    workflow_id: UUID = Field(..., description="Associated workflow ID")
    from_phase: WorkflowPhase = Field(..., description="Previous phase")
    to_phase: WorkflowPhase = Field(..., description="Target phase")
    
    # Transition details
    triggered_by: str = Field(..., description="Who/what triggered the transition")
    trigger_reason: str = Field(..., description="Reason for transition")
    
    # Validation
    dependencies_satisfied: bool = Field(..., description="Whether all dependencies were satisfied")
    validation_passed: bool = Field(..., description="Whether validation passed")
    
    # Timing
    transition_started_at: datetime = Field(default_factory=datetime.utcnow, description="Transition start time")
    transition_completed_at: Optional[datetime] = Field(None, description="Transition completion time")
    
    # Data
    transition_data: Dict[str, Any] = Field(default_factory=dict, description="Transition-specific data")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Validation results")
    
    class Config:
        """Pydantic configuration."""
        
        use_enum_values = True
        validate_assignment = True 