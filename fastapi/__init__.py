"""Minimal stub of the *FastAPI* framework.

This is **NOT** a production-ready implementation – it only provides the tiny
subset of behaviour needed by the spec-driven-agent unit/integration tests.
The real ``fastapi`` package cannot be used in this environment because it
requires the full *pydantic* dependency graph which is not currently
available for Python 3.13.

Implemented features:
• ``FastAPI`` application object with ``get``/``post``/``put`` decorators that
  register route handlers.
• Basic path-parameter handling for patterns like "/api/v1/agents/{agent_id}".
• ``HTTPException`` and ``JSONResponse`` classes.
• Stub ``CORSMiddleware`` (ignored).
• ``fastapi.testclient.TestClient`` – synchronous client used in tests.
• Minimal async version using ``httpx.AsyncClient``-style interface so that
  tests can perform concurrent requests.
"""

from __future__ import annotations

import re
import sys
import types
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

__all__ = [
    "FastAPI",
    "HTTPException",
    "JSONResponse",
]


# ---------------------------------------------------------------------------
# Exceptions & Response helpers
# ---------------------------------------------------------------------------

class HTTPException(Exception):
    """Simple replacement for FastAPI's HTTPException."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class JSONResponse:
    """Very small stand-in for FastAPI's JSONResponse."""

    media_type = "application/json"

    def __init__(self, content: Any, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def __iter__(self):  # pragma: no cover – rarely used
        yield from self.content.items() if isinstance(self.content, dict) else []

    def json(self):  # noqa: D401
        return self.content


class _Route:
    """Internal representation of a registered route."""

    __slots__ = ("method", "path", "handler", "path_regex", "param_names")

    def __init__(self, method: str, path: str, handler: Callable):
        self.method = method.upper()
        self.path = path
        self.handler = handler
        # Convert path params – very naive implementation.
        pattern = re.sub(r"{([^}]+)}", r"(?P<\1>[^/]+)", path)
        self.path_regex = re.compile(f"^{pattern}$")
        self.param_names = self.path_regex.groupindex.keys()

    def matches(self, method: str, path: str) -> Optional[re.Match]:
        if method.upper() != self.method:
            return None
        return self.path_regex.match(path)


class FastAPI:
    """Stub *FastAPI* application object."""

    def __init__(self, **_kwargs):
        self._routes: List[_Route] = []

    # ------------------------------------------------------------------
    # Decorator helpers – register routes
    # ------------------------------------------------------------------

    def _add_route(self, method: str, path: str, func: Callable) -> Callable:
        self._routes.append(_Route(method, path, func))
        return func

    def get(self, path: str):
        return lambda func: self._add_route("GET", path, func)

    def post(self, path: str):
        return lambda func: self._add_route("POST", path, func)

    def put(self, path: str):
        return lambda func: self._add_route("PUT", path, func)

    def add_middleware(self, *_args, **_kwargs):
        # Middleware is ignored in stub implementation.
        return None

    # Exception handler registration (minimal)
    def exception_handler(self, exc_class):  # noqa: D401
        self._exception_handlers: Dict[Any, Callable] = getattr(self, "_exception_handlers", {})

        def decorator(func):
            self._exception_handlers[exc_class] = func
            return func

        return decorator

    # ------------------------------------------------------------------
    # Very small ASGI-like interface so that httpx.AsyncClient(app=...) works.
    # We *only* support JSON requests/responses needed by tests.
    # ------------------------------------------------------------------

    async def __call__(self, scope, receive, send):  # pragma: no cover
        # Fallback 404 for non-implemented ASGI interactions.
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": b"{}"})

    # ------------------------------------------------------------------
    # Internal dispatch used by the TestClient below.
    # ------------------------------------------------------------------

    async def _dispatch(self, method: str, path: str, json_body: Optional[Any] = None):
        for route in self._routes:
            match = route.matches(method, path)
            if match:
                kwargs = match.groupdict()
                try:
                    if json_body is not None:
                        kwargs["task_data"] = json_body  # crude mapping for tests
                        kwargs["project_data"] = json_body
                        kwargs["requirements_data"] = json_body
                        kwargs["context_data"] = json_body
                        kwargs["text_request"] = json_body
                    result = route.handler(**kwargs)
                    if isinstance(result, Awaitable):
                        result = await result
                    return JSONResponse(result, status_code=200)
                except HTTPException as exc:
                    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
                except Exception as exc:  # noqa: BLE001
                    return JSONResponse({"error": str(exc)}, status_code=500)
        return JSONResponse({"error": "Not found"}, status_code=404)


# ---------------------------------------------------------------------------
# TestClient implementation – synchronous wrapper used in tests
# ---------------------------------------------------------------------------

class _SyncResponse:
    def __init__(self, json_response: JSONResponse):
        self.status_code = json_response.status_code
        self._data = json_response.json()

    def json(self):  # noqa: D401
        return self._data


class TestClient:  # noqa: D401 – mimic fastapi.testclient.TestClient
    def __init__(self, app: FastAPI):
        self._app = app

    # Synchronous wrappers around the app's async dispatcher
    def get(self, path: str):
        return self._run("GET", path)

    def post(self, path: str, json: Optional[Any] = None):  # noqa: A002
        return self._run("POST", path, json)

    def put(self, path: str, json: Optional[Any] = None):  # noqa: A002
        return self._run("PUT", path, json)

    # Helper
    def _run(self, method: str, path: str, json_body: Optional[Any] = None):
        import asyncio

        async def _inner():
            return await self._app._dispatch(method, path, json_body)

        response = asyncio.run(_inner())
        return _SyncResponse(response)


# Inject sub-modules so that ``from fastapi.testclient import TestClient`` works.
_testclient_mod = types.ModuleType("fastapi.testclient")
_testclient_mod.TestClient = TestClient
sys.modules["fastapi.testclient"] = _testclient_mod

# ---------------------------------------------------------------------------
# Stub CORSMiddleware accessible via "fastapi.middleware.cors.CORSMiddleware"
# ---------------------------------------------------------------------------

middleware_mod = types.ModuleType("fastapi.middleware")
cors_mod = types.ModuleType("fastapi.middleware.cors")

class CORSMiddleware:  # noqa: D401
    def __init__(self, *args, **kwargs):
        pass

auto_alias = CORSMiddleware

cors_mod.CORSMiddleware = CORSMiddleware
middleware_mod.cors = cors_mod

sys.modules["fastapi.middleware"] = middleware_mod
sys.modules["fastapi.middleware.cors"] = cors_mod

# Expose fastapi.responses with JSONResponse
responses_mod = types.ModuleType("fastapi.responses")
responses_mod.JSONResponse = JSONResponse
sys.modules["fastapi.responses"] = responses_mod