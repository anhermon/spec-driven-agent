"""
Base models and common functionality for the spec-driven agent workflow system.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model with common configuration and fields."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
    )


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentifiableModel(TimestampedModel):
    """Base model with ID field."""

    id: UUID = Field(default_factory=uuid4)


class MetadataModel(IdentifiableModel):
    """Base model with metadata fields."""

    name: str = Field(..., description="Human-readable name")
    description: Optional[str] = Field(None, description="Detailed description")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class StatusModel(MetadataModel):
    """Base model with status tracking."""

    status: str = Field(..., description="Current status")
    status_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status_reason: Optional[str] = Field(None, description="Reason for status change")
