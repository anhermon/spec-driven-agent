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

    # ---------------------------------------------------------------------
    # Pydantic v2 compatibility helpers
    # ---------------------------------------------------------------------
    # The codebase (especially the tests) was originally written targeting
    # Pydantic v2 which introduced the ``model_dump``, ``model_copy`` and
    # ``model_validate`` APIs.  Since we currently rely on Pydantic v1 for
    # Python 3.13 compatibility, we expose shim implementations that delegate
    # to the equivalent v1 helpers so the public surface expected by the tests
    # remains available.

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Alias for :py:meth:`dict` with identical semantics in v1."""

        # ``dict`` in v1 supports nearly the same signature as v2's
        # ``model_dump`` so we just forward the arguments verbatim.
        return self.dict(*args, **kwargs)

    def model_copy(self, *args, **kwargs):  # type: ignore[override]
        """Alias for :py:meth:`copy` with identical semantics in v1."""

        return self.copy(*args, **kwargs)

    @classmethod
    def model_validate(cls, data, *args, **kwargs):  # type: ignore[override]
        """Alias for :py:meth:`parse_obj` to mimic v2 API."""

        return cls.parse_obj(data)


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
