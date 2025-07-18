"""
Task models for the spec-driven agent workflow system.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(StatusModel):
    """Represents the result of a task."""

    task_id: UUID = Field(..., description="Associated task ID")
    result_type: str = Field(..., description="Type of result")

    # Result data
    data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    artifacts: List[str] = Field(
        default_factory=list, description="Generated artifact IDs"
    )

    # Quality metrics
    quality_score: Optional[float] = Field(None, description="Quality score (0-100)")
    validation_passed: bool = Field(
        default=False, description="Whether validation passed"
    )
    validation_errors: List[str] = Field(
        default_factory=list, description="Validation errors"
    )

    # Performance metrics
    execution_time: Optional[float] = Field(
        None, description="Execution time in seconds"
    )
    resource_usage: Dict[str, Any] = Field(
        default_factory=dict, description="Resource usage"
    )

    # Metadata
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Completion timestamp",
    )
    reviewed_by: Optional[UUID] = Field(None, description="Reviewer ID")
    review_notes: Optional[str] = Field(None, description="Review notes")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class TaskDependency(StatusModel):
    """Represents a dependency between tasks."""

    dependency_id: str = Field(..., description="Unique dependency identifier")
    dependent_task_id: UUID = Field(..., description="Task that depends on another")
    prerequisite_task_id: UUID = Field(
        ..., description="Task that must be completed first"
    )

    # Dependency details
    dependency_type: str = Field(default="completion", description="Type of dependency")
    description: str = Field(..., description="Dependency description")

    # Status
    satisfied: bool = Field(
        default=False, description="Whether dependency is satisfied"
    )
    satisfied_at: Optional[datetime] = Field(
        None, description="When dependency was satisfied"
    )

    # Validation
    validation_required: bool = Field(
        default=True, description="Whether validation is required"
    )
    validation_passed: Optional[bool] = Field(None, description="Validation result")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class Task(StatusModel):
    """Represents a task in the spec-driven workflow."""

    # Task identification
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task")
    # Map task_name to name for StatusModel inheritance
    name: str = Field(..., description="Human-readable task name", alias="task_name")
    task_name: str = Field(..., description="Human-readable task name")

    # Task details
    description: str = Field(..., description="Task description")
    requirements: List[str] = Field(
        default_factory=list, description="Task requirements"
    )
    acceptance_criteria: List[str] = Field(
        default_factory=list, description="Acceptance criteria"
    )

    # Assignment and ownership
    assigned_agent_id: Optional[UUID] = Field(None, description="Assigned agent ID")
    created_by: Optional[UUID] = Field(None, description="Task creator ID")
    owner_id: Optional[UUID] = Field(None, description="Task owner ID")

    # Workflow context
    workflow_id: UUID = Field(..., description="Associated workflow ID")
    phase: str = Field(..., description="Workflow phase")
    context_id: Optional[UUID] = Field(None, description="Associated context ID")

    # Dependencies
    dependencies: List[TaskDependency] = Field(
        default_factory=list, description="Task dependencies"
    )
    dependent_tasks: List[UUID] = Field(
        default_factory=list, description="Tasks that depend on this one"
    )

    # Timeline
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    assigned_at: Optional[datetime] = Field(None, description="Assignment timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    due_date: Optional[datetime] = Field(None, description="Due date")

    # Priority and effort
    priority: str = Field(default="medium", description="Task priority")
    effort_estimate: Optional[float] = Field(
        None, description="Effort estimate in hours"
    )
    actual_effort: Optional[float] = Field(None, description="Actual effort in hours")

    # Progress tracking
    progress_percentage: float = Field(default=0.0, description="Progress percentage")
    milestones: List[Dict[str, Any]] = Field(
        default_factory=list, description="Task milestones"
    )
    current_milestone: Optional[str] = Field(None, description="Current milestone")

    # Results and artifacts
    result_id: Optional[UUID] = Field(None, description="Associated result ID")
    artifact_ids: List[UUID] = Field(
        default_factory=list, description="Generated artifact IDs"
    )

    # Communication
    comments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Task comments"
    )
    notifications: List[str] = Field(
        default_factory=list, description="Notification IDs"
    )

    # Configuration
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Task configuration"
    )
    settings: Dict[str, Any] = Field(default_factory=dict, description="Task settings")

    # Status tracking
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    status_reason: Optional[str] = Field(None, description="Reason for status change")
    status_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Status history"
    )

    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )
    quality_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Quality metrics"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
        populate_by_name = True

    def __init__(self, **data):
        # Ensure task_name is mapped to name for StatusModel inheritance
        if "task_name" in data and "name" not in data:
            data["name"] = data["task_name"]
        super().__init__(**data)
