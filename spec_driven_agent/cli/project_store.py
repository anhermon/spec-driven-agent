from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from ..models.project import Project

# Directory where project definitions are stored per-user
_PROJECTS_DIR = Path.home() / ".specdriven" / "projects"


def _ensure_dir() -> None:
    """Ensure the projects directory exists."""
    _PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def project_file_path(project_id: str) -> Path:
    """Return the path of the JSON file that stores a project."""
    return _PROJECTS_DIR / f"{project_id}.json"


def save_project(project: Project, extra: Optional[dict] = None) -> Path:
    """Serialize a Project (and optional extra data) to disk and return file path."""
    _ensure_dir()
    data = project.model_dump(mode="json")  # type: ignore[arg-type]
    if extra:
        data["_extra"] = extra  # namespaced to avoid collisions
    path = project_file_path(str(project.id))
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)
    return path


def load_project(project_id: str) -> Optional[Project]:
    """Load a project by id. Returns None if not found or corrupted."""
    path = project_file_path(project_id)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        # Remove internal key if present
        data.pop("_extra", None)
        return Project.model_validate(data)  # type: ignore[call-arg]
    except Exception:
        return None


def list_projects() -> List[Project]:
    """Return all saved projects."""
    _ensure_dir()
    projects: List[Project] = []
    for file in _PROJECTS_DIR.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            data.pop("_extra", None)
            projects.append(Project.model_validate(data))  # type: ignore[call-arg]
        except Exception:
            # Skip unreadable files
            continue
    return projects


def delete_project(project_id: str) -> bool:
    """Delete a project file. Returns True if deleted."""
    path = project_file_path(project_id)
    if path.exists():
        try:
            path.unlink()
            return True
        except Exception:
            return False
    return False