"""
Context models for the spec-driven agent workflow system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class AgentContext(StatusModel):
    """Represents the context for an individual agent."""
    
    agent_id: str = Field(..., description="Agent identifier")
    context_id: UUID = Field(..., description="Unique context identifier")
    
    # Agent-specific data
    agent_data: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific data")
    agent_state: Dict[str, Any] = Field(default_factory=dict, description="Agent state information")
    
    # Project context reference
    project_context_id: Optional[UUID] = Field(None, description="Reference to project context")
    
    # Communication context
    message_history: List[Dict[str, Any]] = Field(default_factory=list, description="Message history")
    active_conversations: List[str] = Field(default_factory=list, description="Active conversation IDs")
    
    # Task context
    current_task_id: Optional[str] = Field(None, description="Current task ID")
    task_history: List[str] = Field(default_factory=list, description="Task history")
    
    # Performance and monitoring
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    activity_count: int = Field(default=0, description="Activity count")
    
    class Config:
        """Pydantic configuration."""
        
        validate_assignment = True


class SymbolicReference(StatusModel):
    """Represents a symbolic reference to data in the context."""
    
    reference_id: str = Field(..., description="Unique reference identifier")
    reference_type: str = Field(..., description="Type of reference (e.g., 'api_spec', 'requirement')")
    target_id: Optional[UUID] = Field(None, description="Target object ID")
    target_path: Optional[str] = Field(None, description="Path to target data")
    
    # Symbolic properties
    symbolic_name: str = Field(..., description="Symbolic name for the reference")
    symbolic_type: str = Field(..., description="Symbolic type classification")
    symbolic_properties: Dict[str, Any] = Field(default_factory=dict, description="Symbolic properties")
    
    # Resolution
    resolved: bool = Field(default=False, description="Whether reference is resolved")
    resolved_at: Optional[datetime] = Field(None, description="When reference was resolved")
    resolution_data: Optional[Dict[str, Any]] = Field(None, description="Resolution data")
    
    # Consistency
    consistency_checks: List[str] = Field(default_factory=list, description="Applied consistency checks")
    consistency_status: str = Field(default="pending", description="Consistency status")
    
    class Config:
        """Pydantic configuration."""
        
        validate_assignment = True


class SymbolicData(StatusModel):
    """Represents symbolic data in the context."""
    
    symbolic_id: str = Field(..., description="Unique symbolic identifier")
    symbolic_type: str = Field(..., description="Type of symbolic data")
    symbolic_name: str = Field(..., description="Symbolic name")
    
    # Data representation
    concrete_data: Optional[Any] = Field(None, description="Concrete data representation")
    symbolic_representation: Dict[str, Any] = Field(default_factory=dict, description="Symbolic representation")
    
    # Relationships
    parent_symbolic_id: Optional[str] = Field(None, description="Parent symbolic data ID")
    child_symbolic_ids: List[str] = Field(default_factory=list, description="Child symbolic data IDs")
    related_symbolic_ids: List[str] = Field(default_factory=list, description="Related symbolic data IDs")
    
    # Metadata
    creation_context: Dict[str, Any] = Field(default_factory=dict, description="Context when created")
    last_accessed: datetime = Field(default_factory=datetime.utcnow, description="Last access time")
    access_count: int = Field(default=0, description="Number of times accessed")
    
    # Validation
    validation_status: str = Field(default="pending", description="Validation status")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    class Config:
        """Pydantic configuration."""
        
        validate_assignment = True


class ContextUpdate(StatusModel):
    """Represents an update to the context."""
    
    context_id: UUID = Field(..., description="Target context ID")
    update_type: str = Field(..., description="Type of update")
    
    # Update data
    update_data: Dict[str, Any] = Field(..., description="Update data")
    update_path: Optional[str] = Field(None, description="Path to update location")
    
    # Source information
    source_agent_id: Optional[UUID] = Field(None, description="Source agent ID")
    source_user_id: Optional[UUID] = Field(None, description="Source user ID")
    source_type: str = Field(..., description="Source type (agent, user, system)")
    
    # Validation
    validation_required: bool = Field(default=True, description="Whether validation is required")
    validation_passed: Optional[bool] = Field(None, description="Validation result")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    # Processing
    processed: bool = Field(default=False, description="Whether update has been processed")
    processed_at: Optional[datetime] = Field(None, description="When update was processed")
    processing_errors: List[str] = Field(default_factory=list, description="Processing errors")
    
    # Consistency
    consistency_impact: str = Field(default="unknown", description="Impact on context consistency")
    consistency_checks: List[str] = Field(default_factory=list, description="Required consistency checks")
    
    class Config:
        """Pydantic configuration."""
        
        validate_assignment = True


class SpecDrivenContext(StatusModel):
    """Represents the spec-driven context for a project."""
    
    # Context identification
    project_id: UUID = Field(..., description="Associated project ID")
    context_type: str = Field(default="spec_driven", description="Context type")
    
    # Core context data
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Project requirements")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="API specifications")
    architecture: Dict[str, Any] = Field(default_factory=dict, description="System architecture")
    implementation: Dict[str, Any] = Field(default_factory=dict, description="Implementation details")
    
    # Symbolic mechanisms
    symbolic_data: Dict[str, SymbolicData] = Field(default_factory=dict, description="Symbolic data")
    symbolic_references: Dict[str, SymbolicReference] = Field(default_factory=dict, description="Symbolic references")
    
    # Context relationships
    parent_context_id: Optional[UUID] = Field(None, description="Parent context ID")
    child_context_ids: List[UUID] = Field(default_factory=list, description="Child context IDs")
    related_context_ids: List[UUID] = Field(default_factory=list, description="Related context IDs")
    
    # History and versioning
    version: int = Field(default=1, description="Context version")
    version_history: List[Dict[str, Any]] = Field(default_factory=list, description="Version history")
    update_history: List[UUID] = Field(default_factory=list, description="Update history IDs")
    
    # Consistency and validation
    consistency_status: str = Field(default="pending", description="Overall consistency status")
    consistency_checks: List[str] = Field(default_factory=list, description="Applied consistency checks")
    consistency_errors: List[str] = Field(default_factory=list, description="Consistency errors")
    
    # Access control
    read_access: List[UUID] = Field(default_factory=list, description="Read access user/agent IDs")
    write_access: List[UUID] = Field(default_factory=list, description="Write access user/agent IDs")
    
    # Performance and caching
    cache_key: Optional[str] = Field(None, description="Cache key for performance")
    last_consistency_check: Optional[datetime] = Field(None, description="Last consistency check time")
    consistency_check_duration: Optional[float] = Field(None, description="Consistency check duration")
    
    class Config:
        """Pydantic configuration."""
        
        validate_assignment = True


class ContextConsistencyValidator(StatusModel):
    """Represents a context consistency validator."""
    
    validator_id: str = Field(..., description="Unique validator identifier")
    validator_type: str = Field(..., description="Type of validator")
    validator_name: str = Field(..., description="Human-readable validator name")
    
    # Validation rules
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Validation rules")
    validation_config: Dict[str, Any] = Field(default_factory=dict, description="Validation configuration")
    
    # Performance
    execution_time: Optional[float] = Field(None, description="Last execution time")
    average_execution_time: Optional[float] = Field(None, description="Average execution time")
    execution_count: int = Field(default=0, description="Number of executions")
    
    # Results
    last_validation_result: Optional[Dict[str, Any]] = Field(None, description="Last validation result")
    validation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Validation history")
    
    # Status
    enabled: bool = Field(default=True, description="Whether validator is enabled")
    priority: int = Field(default=1, description="Validator priority (lower = higher priority)")
    
    class Config:
        """Pydantic configuration."""
        
        validate_assignment = True 