"""A very small stub of the `pydantic` API.

This stub is NOT a full replacement for the real ``pydantic`` package – it only implements
just enough behaviour for the spec-driven-agent test-suite to run under environments where
installing the real package is impossible (e.g. Python 3.13 where PyO3 wheels are not yet
available).

Implemented pieces:
• ValidationError – simple subclass of ``Exception``.
• ConfigDict      – alias of ``dict`` to keep type-checking happy.
• Field(...)      – captures metadata for a schema field.
• BaseModel       – very small dataclass-style container with:
                   - required/optional field handling
                   - attribute validation for required fields
                   - ``model_dump`` / ``dict``
                   - ``model_copy``
                   - ``model_validate`` class-method
The implementation purposefully ignores many advanced pydantic features (type coercion,
validators, alias mapping, etc.) because they are not needed by the current tests.
"""

from __future__ import annotations

import copy
import inspect
from types import MappingProxyType
from typing import Any, Dict, Optional, Callable

__all__ = [
    "BaseModel",
    "Field",
    "ConfigDict",
    "ValidationError",
]

# ---------------------------------------------------------------------------
# Public symbols
# ---------------------------------------------------------------------------

ValidationError = type("ValidationError", (Exception,), {})  # Simple alias

# ConfigDict is used purely as a *type* in code-base – alias to `dict` is fine.
ConfigDict = dict  # type: ignore

# Sentinel used to mark required fields (equivalent to `...` in real pydantic).
_REQUIRED = Ellipsis


class FieldInfo:
    """Lightweight stand-in for pydantic's FieldInfo object."""

    __slots__ = ("default", "default_factory", "description", "alias")

    def __init__(
        self,
        default: Any = _REQUIRED,
        *,
        default_factory: Optional[Callable[[], Any]] = None,
        description: Optional[str] = None,
        alias: Optional[str] = None,
        **_ignored: Any,
    ) -> None:
        if default is not _REQUIRED and default_factory is not None:
            raise ValueError("Specify either default or default_factory, not both")
        self.default = default
        self.default_factory = default_factory
        self.description = description
        self.alias = alias

    # The real pydantic FieldInfo is callable – we don't need that here.


def Field(
    default: Any = _REQUIRED,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    description: Optional[str] = None,
    alias: Optional[str] = None,
    **kwargs: Any,
) -> FieldInfo:  # noqa: D401 – keep same signature style as pydantic
    """Return a *FieldInfo* instance describing a model field.

    Only a subset of pydantic's keyword arguments is recognised – the rest are
    accepted and ignored so that the call-sites remain compatible.
    """

    return FieldInfo(
        default=default,
        default_factory=default_factory,
        description=description,
        alias=alias,
        **kwargs,
    )


class BaseModelMeta(type):
    """Metaclass that processes *FieldInfo* declarations on class creation."""

    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        annotations: Dict[str, Any] = namespace.get("__annotations__", {})
        # Collect fields from base classes first (to support inheritance)
        combined_fields: Dict[str, FieldInfo] = {}
        for base in bases:
            if hasattr(base, "__fields__"):
                combined_fields.update(base.__fields__)  # type: ignore[attr-defined]

        # Process declarations in *namespace*
        for attr_name, type_hint in annotations.items():
            value = namespace.get(attr_name, _REQUIRED)
            if isinstance(value, FieldInfo):
                field_info = value
            else:
                # Not a Field(...) – treat value as default, infer required flag
                default_val = value if value is not _REQUIRED else _REQUIRED
                field_info = FieldInfo(default=default_val)
            combined_fields[attr_name] = field_info

        if "__fields__" in combined_fields:
            combined_fields.pop("__fields__")

        namespace["__fields__"] = MappingProxyType(combined_fields)
        return super().__new__(mcls, name, bases, namespace)


class BaseModel(metaclass=BaseModelMeta):
    """Very small subset of *pydantic.BaseModel* functionality."""

    __fields__: Dict[str, FieldInfo]  # populated via metaclass

    def __init__(self, **data: Any):  # noqa: D401 – keep signature compatible
        missing = []
        for field_name, field_info in self.__fields__.items():
            if field_name in data:
                value = data.pop(field_name)
            elif field_info.alias and field_info.alias in data:
                value = data.pop(field_info.alias)
            elif field_info.default is not _REQUIRED or field_info.default_factory is not None:
                value = (
                    field_info.default
                    if field_info.default is not _REQUIRED
                    else field_info.default_factory() if field_info.default_factory else None
                )
            else:
                missing.append(field_name)
                continue
            setattr(self, field_name, value)

        if missing:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing)} in {self.__class__.__name__}"
            )
        # Any extra keys – store as attributes as well to keep behaviour flexible
        for extra_key, extra_val in data.items():
            setattr(self, extra_key, extra_val)

    # ------------------------------------------------------------------
    # API helpers expected by the test-suite
    # ------------------------------------------------------------------

    def model_dump(self, *_, **__) -> Dict[str, Any]:  # ignore args
        """Return a shallow dict of model data (like pydantic v2)."""
        return {k: getattr(self, k) for k in self.__fields__}

    # Alias for compatibility with pydantic v1 `.dict()`
    dict = model_dump  # type: ignore[assignment]

    def model_copy(self, *, deep: bool = False) -> "BaseModel":
        """Return a copy of the model (deep if requested)."""
        return copy.deepcopy(self) if deep else copy.copy(self)

    @classmethod
    def model_validate(cls, data: Any) -> "BaseModel":
        """Create a model instance from a dict or another model."""
        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise ValidationError("model_validate expects a mapping or model instance")
        return cls(**data)

    # ------------------------------------------------------------------
    # Convenience dunders – not exactly pydantic behaviour but adequate.
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # noqa: D401 – double quotes avoid escape issues
        fields_repr = ", ".join(f"{k}={repr(getattr(self, k, None))}" for k in self.__fields__)
        return f"{self.__class__.__name__}({fields_repr})"

    def __str__(self) -> str:
        return repr(self)

    # Equality: shallow compare by all declared fields
    def __eq__(self, other: object) -> bool:  # noqa: D401
        if not isinstance(other, self.__class__):
            return False
        return all(
            getattr(self, fname, None) == getattr(other, fname, None) for fname in self.__fields__
        )

__all__.append("create_model")

def create_model(model_name: str, **field_definitions: Any):  # noqa: D401
    """A *very* small subset of pydantic.create_model.

    Usage examples in FastAPI mostly rely on dynamic model creation for examples
    or request bodies.  We simply generate a new subclass of ``BaseModel`` with
    the provided *field_definitions* converted into ``FieldInfo`` instances when
    necessary.
    """

    namespace: Dict[str, Any] = {"__annotations__": {}}
    for field_name, value in field_definitions.items():
        if isinstance(value, tuple):
            # expected pattern: (<type>, <default value or Field(...))
            type_hint, default_value = value
        else:
            # if only a type is provided treat as required
            type_hint, default_value = value, _REQUIRED

        namespace["__annotations__"][field_name] = type_hint
        if not isinstance(default_value, FieldInfo):
            default_value = Field(default_value)
        namespace[field_name] = default_value

    return BaseModelMeta(model_name, (BaseModel,), namespace)

# ------------------------------------------------------------------
# Provide `pydantic.version.VERSION` so that FastAPI can introspect the
# installed pydantic version.
# ------------------------------------------------------------------
import sys
import types

_version_mod = types.ModuleType("pydantic.version")
_version_mod.VERSION = "2.0.0-stub"

sys.modules["pydantic.version"] = _version_mod

# Additional exception class expected by FastAPI
class PydanticSchemaGenerationError(Exception):
    """Stub for FastAPI compatibility (schema generation errors)."""

__all__.append("PydanticSchemaGenerationError")

class TypeAdapter:  # pragma: no cover
    """Simplistic placeholder to satisfy FastAPI import paths."""

    def __init__(self, _type: Any, *args: Any, **kwargs: Any):
        self.type = _type

    def validate_python(self, value: Any, *args: Any, **kwargs: Any) -> Any:  # noqa: D401
        return value

__all__.append("TypeAdapter")