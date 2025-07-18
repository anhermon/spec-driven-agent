"""Utility to export the OpenAPI schema for the FastAPI application.

Run:
    python docs/generate_openapi.py

Outputs `openapi.json` and `openapi.yaml` to `docs/api/`.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml  # type: ignore
from fastapi.testclient import TestClient

# Importing here allows script execution without setting PYTHONPATH if run from repo root
from spec_driven_agent.main import app  # noqa: E402  pylint: disable=wrong-import-position


def main() -> None:  # pragma: no cover
    """Generate OpenAPI schema and write to docs/api/."""
    client = TestClient(app)

    # Ensure the schema is generated (FastAPI caches it).
    _ = client.get("/openapi.json")

    schema = app.openapi()

    target_dir = Path(__file__).parent / "api"
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "openapi.json"
    json_path.write_text(json.dumps(schema, indent=2))

    yaml_path = target_dir / "openapi.yaml"
    yaml_path.write_text(yaml.safe_dump(schema, sort_keys=False))

    print(f"✅ OpenAPI schema written to {json_path} and {yaml_path}")


if __name__ == "__main__":
    main()