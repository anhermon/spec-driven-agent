"""
Specification models for the spec-driven agent workflow system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class OpenAPISpec(StatusModel):
    """Represents an OpenAPI specification."""

    # Specification identification
    spec_id: str = Field(..., description="Unique specification identifier")
    spec_version: str = Field(..., description="OpenAPI version")
    spec_name: str = Field(..., description="Specification name")

    # OpenAPI structure
    info: Dict[str, Any] = Field(..., description="API information")
    paths: Dict[str, Any] = Field(default_factory=dict, description="API paths")
    components: Dict[str, Any] = Field(
        default_factory=dict, description="API components"
    )
    security: List[Dict[str, Any]] = Field(
        default_factory=list, description="Security schemes"
    )

    # Metadata
    tags: List[Dict[str, Any]] = Field(default_factory=list, description="API tags")
    external_docs: Optional[Dict[str, Any]] = Field(
        None, description="External documentation"
    )

    # Validation
    validation_status: str = Field(default="pending", description="Validation status")
    validation_errors: List[str] = Field(
        default_factory=list, description="Validation errors"
    )
    validation_warnings: List[str] = Field(
        default_factory=list, description="Validation warnings"
    )

    # Relationships
    project_id: UUID = Field(..., description="Associated project ID")
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    parent_spec_id: Optional[str] = Field(None, description="Parent specification ID")

    # Versioning
    version: str = Field(default="1.0.0", description="Specification version")
    version_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Version history"
    )

    # Generation
    generated_by: Optional[str] = Field(None, description="Generation source")
    generation_config: Dict[str, Any] = Field(
        default_factory=dict, description="Generation configuration"
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class Requirements(StatusModel):
    """Represents project requirements."""

    # Requirements identification
    requirements_id: str = Field(..., description="Unique requirements identifier")
    requirements_type: str = Field(
        default="functional", description="Type of requirements"
    )

    # Requirements content
    functional_requirements: List[Dict[str, Any]] = Field(
        default_factory=list, description="Functional requirements"
    )
    non_functional_requirements: List[Dict[str, Any]] = Field(
        default_factory=list, description="Non-functional requirements"
    )
    user_stories: List[Dict[str, Any]] = Field(
        default_factory=list, description="User stories"
    )
    acceptance_criteria: List[Dict[str, Any]] = Field(
        default_factory=list, description="Acceptance criteria"
    )

    # Stakeholder information
    stakeholders: List[Dict[str, Any]] = Field(
        default_factory=list, description="Stakeholder information"
    )
    business_rules: List[str] = Field(
        default_factory=list, description="Business rules"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Project constraints"
    )

    # Priority and categorization
    priority_levels: Dict[str, str] = Field(
        default_factory=dict, description="Priority levels"
    )
    categories: List[str] = Field(
        default_factory=list, description="Requirement categories"
    )
    tags: List[str] = Field(default_factory=list, description="Requirement tags")

    # Validation and approval
    validation_status: str = Field(default="pending", description="Validation status")
    approval_status: str = Field(default="pending", description="Approval status")
    approved_by: Optional[UUID] = Field(None, description="Approver ID")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")

    # Relationships
    project_id: UUID = Field(..., description="Associated project ID")
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    derived_specs: List[str] = Field(
        default_factory=list, description="Derived specification IDs"
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class Architecture(StatusModel):
    """Represents system architecture."""

    # Architecture identification
    architecture_id: str = Field(..., description="Unique architecture identifier")
    architecture_type: str = Field(default="system", description="Type of architecture")

    # Architecture components
    components: List[Dict[str, Any]] = Field(
        default_factory=list, description="System components"
    )
    layers: List[Dict[str, Any]] = Field(
        default_factory=list, description="Architecture layers"
    )
    patterns: List[Dict[str, Any]] = Field(
        default_factory=list, description="Design patterns"
    )
    technologies: List[Dict[str, Any]] = Field(
        default_factory=list, description="Technology stack"
    )

    # System design
    system_overview: Dict[str, Any] = Field(
        default_factory=dict, description="System overview"
    )
    data_flow: List[Dict[str, Any]] = Field(
        default_factory=list, description="Data flow diagrams"
    )
    interfaces: List[Dict[str, Any]] = Field(
        default_factory=list, description="System interfaces"
    )
    security_model: Dict[str, Any] = Field(
        default_factory=dict, description="Security model"
    )

    # Quality attributes
    quality_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Quality attributes"
    )
    performance_requirements: Dict[str, Any] = Field(
        default_factory=dict, description="Performance requirements"
    )
    scalability_requirements: Dict[str, Any] = Field(
        default_factory=dict, description="Scalability requirements"
    )

    # Validation and review
    validation_status: str = Field(default="pending", description="Validation status")
    review_status: str = Field(default="pending", description="Review status")
    reviewed_by: Optional[UUID] = Field(None, description="Reviewer ID")
    review_notes: Optional[str] = Field(None, description="Review notes")

    # Relationships
    project_id: UUID = Field(..., description="Associated project ID")
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    requirements_id: Optional[str] = Field(
        None, description="Associated requirements ID"
    )
    derived_implementations: List[str] = Field(
        default_factory=list, description="Derived implementation IDs"
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


class Implementation(StatusModel):
    """Represents implementation details."""

    # Implementation identification
    implementation_id: str = Field(..., description="Unique implementation identifier")
    implementation_type: str = Field(
        default="code", description="Type of implementation"
    )

    # Implementation structure
    modules: List[Dict[str, Any]] = Field(
        default_factory=list, description="Code modules"
    )
    files: List[Dict[str, Any]] = Field(
        default_factory=list, description="Implementation files"
    )
    dependencies: List[Dict[str, Any]] = Field(
        default_factory=list, description="Dependencies"
    )
    tests: List[Dict[str, Any]] = Field(
        default_factory=list, description="Test specifications"
    )

    # Code quality
    code_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Code quality metrics"
    )
    test_coverage: Optional[float] = Field(None, description="Test coverage percentage")
    code_review_status: str = Field(default="pending", description="Code review status")

    # Build and deployment
    build_config: Dict[str, Any] = Field(
        default_factory=dict, description="Build configuration"
    )
    deployment_config: Dict[str, Any] = Field(
        default_factory=dict, description="Deployment configuration"
    )
    environment_config: Dict[str, Any] = Field(
        default_factory=dict, description="Environment configuration"
    )

    # Performance and monitoring
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Performance metrics"
    )
    monitoring_config: Dict[str, Any] = Field(
        default_factory=dict, description="Monitoring configuration"
    )

    # Validation and testing
    validation_status: str = Field(default="pending", description="Validation status")
    test_status: str = Field(default="pending", description="Test status")
    test_results: Dict[str, Any] = Field(
        default_factory=dict, description="Test results"
    )

    # Relationships
    project_id: UUID = Field(..., description="Associated project ID")
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    architecture_id: Optional[str] = Field(
        None, description="Associated architecture ID"
    )
    spec_id: Optional[str] = Field(None, description="Associated specification ID")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
