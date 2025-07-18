"""sitecustomize module automatically loaded by Python to apply runtime patches.

This patch ensures compatibility between Pydantic v1 and Python 3.13 by
updating the internal `evaluate_forwardref` helper to work with the new
`typing.ForwardRef._evaluate` signature which now requires a
`recursive_guard` keyword-only argument.

Importing this module happens implicitly at interpreter start-up, so the patch
is applied before libraries such as FastAPI import Pydantic and thus prevents
import-time errors.
"""
from __future__ import annotations

import typing

# ---------------------------------------------------------------------------
# Python 3.13 forward-reference compatibility shim
# ---------------------------------------------------------------------------

# In 3.13 the private signature of ``typing.ForwardRef._evaluate`` changed to
# include a mandatory ``recursive_guard`` kw-only parameter.  Older third-party
# libraries (e.g. Pydantic < 2) still invoke it with the legacy positional
# signature which now raises ``TypeError``.  To maintain backwards
# compatibility we replace ``ForwardRef._evaluate`` with a thin wrapper that
# injects the missing argument when absent.  This avoids touching individual
# libraries and works regardless of the import order.

_orig_forward_evaluate = typing.ForwardRef._evaluate  # type: ignore[attr-defined]


def _forwardref_evaluate_shim(
    self: typing.ForwardRef,
    globalns: dict | None,
    localns: dict | None,
    *args,  # ``type_params`` in CPython implementation (ignored by Pydantic)
    **kwargs,  # may include ``recursive_guard`` in modern callers
):
    if "recursive_guard" not in kwargs:
        kwargs["recursive_guard"] = set()
    return _orig_forward_evaluate(self, globalns, localns, *args, **kwargs)  # type: ignore[arg-type]


# Apply the monkey-patch once.
typing.ForwardRef._evaluate = _forwardref_evaluate_shim  # type: ignore[attr-defined]

print("[sitecustomize] ForwardRef._evaluate patched for compatibility")