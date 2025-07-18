"""Stub module for *uvicorn* to satisfy import in tests."""

def run(*_args, **_kwargs):  # noqa: D401 – no-op stub
    print("[uvicorn stub] run() called – ignoring as not needed in tests.")