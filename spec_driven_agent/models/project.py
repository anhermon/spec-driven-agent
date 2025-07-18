"""
Project models for the spec-driven agent workflow system.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from .base import StatusModel


class ProjectStatus(str):
    """Project status enumeration."""

    DRAFT = "draft"
    PLANNING = "planning"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class Project(StatusModel):
    """Represents a development project in the spec-driven workflow."""

    # Project identification
    name: str = Field(..., description="Project name")
    slug: str = Field(..., description="URL-friendly project identifier")

    # Project details
    description: str = Field(..., description="Project description")
    business_case: Optional[str] = Field(
        None, description="Business case and justification"
    )

    # Stakeholder information
    stakeholders: List[str] = Field(
        default_factory=list, description="List of stakeholder names"
    )
    product_owner: Optional[str] = Field(None, description="Product owner name")

    # Technical constraints
    technical_constraints: List[str] = Field(
        default_factory=list, description="Technical constraints and requirements"
    )
    non_functional_requirements: List[str] = Field(
        default_factory=list, description="Non-functional requirements"
    )

    # Timeline and milestones
    target_completion_date: Optional[datetime] = Field(
        None, description="Target completion date"
    )
    milestones: List[str] = Field(
        default_factory=list, description="Project milestones"
    )

    # Team and resources
    team_size: Optional[int] = Field(None, description="Expected team size")
    budget: Optional[float] = Field(None, description="Project budget")

    # Workflow tracking
    current_phase: str = Field(
        default=ProjectStatus.DRAFT, description="Current workflow phase"
    )
    workflow_instance_id: Optional[UUID] = Field(
        None, description="Associated workflow instance"
    )

    # Context and artifacts
    context_id: Optional[UUID] = Field(None, description="Associated context ID")
    artifact_ids: List[UUID] = Field(
        default_factory=list, description="List of artifact IDs"
    )

    # Metadata
    tags: List[str] = Field(
        default_factory=list, description="Project tags for categorization"
    )
    priority: str = Field(
        default="medium", description="Project priority (low, medium, high, critical)"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
