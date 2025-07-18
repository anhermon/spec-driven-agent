from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from ..models.workflow import WorkflowInstance

_WORKFLOWS_DIR = Path.home() / ".specdriven" / "workflows"


def _ensure_dir() -> None:
    _WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)


def workflow_file_path(workflow_id: str) -> Path:
    return _WORKFLOWS_DIR / f"{workflow_id}.json"


def save_workflow(workflow: WorkflowInstance) -> Path:
    _ensure_dir()
    path = workflow_file_path(str(workflow.id))
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(workflow.model_dump(mode="json"), fp, indent=2)
    return path


def load_workflow(workflow_id: str) -> Optional[WorkflowInstance]:
    path = workflow_file_path(workflow_id)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return WorkflowInstance.model_validate(data)  # type: ignore[call-arg]
    except Exception:
        return None


def list_workflows() -> List[WorkflowInstance]:
    _ensure_dir()
    items: List[WorkflowInstance] = []
    for f in _WORKFLOWS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            items.append(WorkflowInstance.model_validate(data))  # type: ignore[call-arg]
        except Exception:
            continue
    return items