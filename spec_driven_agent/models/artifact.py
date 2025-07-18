"""
Artifact models for the spec-driven agent workflow system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class ArtifactType(str):
    """Artifact type enumeration."""

    DOCUMENT = "document"
    CODE = "code"
    SPECIFICATION = "specification"
    DIAGRAM = "diagram"
    TEST = "test"
    CONFIGURATION = "configuration"
    DATA = "data"
    REPORT = "report"
    TEMPLATE = "template"
    OTHER = "other"


class ArtifactMetadata(StatusModel):
    """Represents metadata for an artifact."""

    artifact_id: UUID = Field(..., description="Associated artifact ID")
    metadata_type: str = Field(..., description="Type of metadata")

    # Content metadata
    content_type: str = Field(..., description="Content type")
    encoding: str = Field(default="utf-8", description="Content encoding")
    language: Optional[str] = Field(None, description="Programming language")
    framework: Optional[str] = Field(None, description="Framework used")

    # Quality metrics
    quality_score: Optional[float] = Field(None, description="Quality score (0-100)")
    complexity_score: Optional[float] = Field(None, description="Complexity score")
    maintainability_score: Optional[float] = Field(
        None, description="Maintainability score"
    )

    # Validation
    validation_status: str = Field(default="pending", description="Validation status")
    validation_errors: List[str] = Field(
        default_factory=list, description="Validation errors"
    )
    validation_warnings: List[str] = Field(
        default_factory=list, description="Validation warnings"
    )

    # Usage tracking
    usage_count: int = Field(default=0, description="Number of times used")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")
    access_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Access history"
    )

    # Relationships
    dependencies: List[str] = Field(
        default_factory=list, description="Dependency artifact IDs"
    )
    derived_from: List[str] = Field(
        default_factory=list, description="Source artifact IDs"
    )
    derived_to: List[str] = Field(
        default_factory=list, description="Derived artifact IDs"
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class Artifact(StatusModel):
    """Represents an artifact in the spec-driven workflow."""

    # Artifact identification
    artifact_id: str = Field(..., description="Unique artifact identifier")
    artifact_type: ArtifactType = Field(..., description="Type of artifact")
    artifact_name: str = Field(..., description="Human-readable artifact name")

    # Content and storage
    content: Optional[str] = Field(None, description="Artifact content")
    file_path: Optional[str] = Field(None, description="File path if stored as file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="Content checksum")

    # Generation and ownership
    generated_by: Optional[UUID] = Field(None, description="Generator agent ID")
    generated_from: Optional[str] = Field(
        None, description="Source specification or requirement"
    )
    generation_config: Dict[str, Any] = Field(
        default_factory=dict, description="Generation configuration"
    )

    # Workflow context
    project_id: UUID = Field(..., description="Associated project ID")
    workflow_id: Optional[UUID] = Field(None, description="Associated workflow ID")
    phase: str = Field(..., description="Workflow phase")
    task_id: Optional[UUID] = Field(None, description="Associated task ID")

    # Versioning
    version: str = Field(default="1.0.0", description="Artifact version")
    version_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Version history"
    )
    parent_version: Optional[str] = Field(None, description="Parent version ID")

    # Quality and validation
    quality_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Quality metrics"
    )
    validation_status: str = Field(default="pending", description="Validation status")
    review_status: str = Field(default="pending", description="Review status")
    approved_by: Optional[UUID] = Field(None, description="Approver ID")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")

    # Usage and lifecycle
    lifecycle_stage: str = Field(default="draft", description="Lifecycle stage")
    usage_count: int = Field(default=0, description="Usage count")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")

    # Relationships
    dependencies: List[str] = Field(
        default_factory=list, description="Dependency artifact IDs"
    )
    related_artifacts: List[str] = Field(
        default_factory=list, description="Related artifact IDs"
    )
    superseded_by: Optional[str] = Field(None, description="Superseding artifact ID")
    supersedes: List[str] = Field(
        default_factory=list, description="Superseded artifact IDs"
    )

    # Access control
    read_access: List[UUID] = Field(
        default_factory=list, description="Read access user/agent IDs"
    )
    write_access: List[UUID] = Field(
        default_factory=list, description="Write access user/agent IDs"
    )
    delete_access: List[UUID] = Field(
        default_factory=list, description="Delete access user/agent IDs"
    )

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Artifact tags")
    categories: List[str] = Field(
        default_factory=list, description="Artifact categories"
    )
    description: str = Field(..., description="Artifact description")

    # Performance and monitoring
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )
    monitoring_config: Dict[str, Any] = Field(
        default_factory=dict, description="Monitoring configuration"
    )

    # Configuration
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Artifact configuration"
    )
    settings: Dict[str, Any] = Field(
        default_factory=dict, description="Artifact settings"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
