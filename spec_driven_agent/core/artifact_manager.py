"""
Artifact Manager for managing generated artifacts in the spec-driven workflow.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ..models.artifact import Artifact, ArtifactMetadata, ArtifactType


class ArtifactManager:
    """
    Manages artifacts generated during the spec-driven workflow.

    Handles artifact creation, storage, retrieval, versioning, and
    relationship management.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the artifact manager."""
        self.storage_path = Path(storage_path) if storage_path else Path("./artifacts")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.artifacts: Dict[str, Artifact] = {}
        self.metadata: Dict[UUID, ArtifactMetadata] = {}
        self.relationships: Dict[str, List[str]] = {}

    async def create_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_name: str,
        content: str,
        project_id: UUID,
        phase: str,
        generated_by: Optional[UUID] = None,
        **kwargs,
    ) -> Artifact:
        """
        Create a new artifact.

        Args:
            artifact_type: Type of artifact
            artifact_name: Name of the artifact
            content: Artifact content
            project_id: Associated project ID
            phase: Workflow phase
            generated_by: Generator agent ID
            **kwargs: Additional artifact properties

        Returns:
            The created artifact
        """
        artifact_id = str(uuid4())

        # Calculate checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()

        # Create artifact
        artifact = Artifact(
            id=uuid4(),
            name=artifact_name,
            description=kwargs.get("description", f"{artifact_type} artifact"),
            status="active",
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            artifact_name=artifact_name,
            content=content,
            checksum=checksum,
            file_size=len(content.encode()),
            generated_by=generated_by,
            project_id=project_id,
            phase=phase,
            **kwargs,
        )

        # Store artifact
        self.artifacts[artifact_id] = artifact

        # Create metadata
        metadata = await self._create_metadata(artifact)
        self.metadata[artifact.id] = metadata

        # Save to file system
        await self._save_artifact_to_file(artifact)

        return artifact

    async def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """
        Get artifact by ID.

        Args:
            artifact_id: The artifact ID to retrieve

        Returns:
            The artifact if found, None otherwise
        """
        return self.artifacts.get(artifact_id)

    async def update_artifact(
        self, artifact_id: str, content: str, **kwargs
    ) -> Optional[Artifact]:
        """
        Update an existing artifact.

        Args:
            artifact_id: The artifact ID to update
            content: New content
            **kwargs: Additional properties to update

        Returns:
            The updated artifact if found, None otherwise
        """
        artifact = await self.get_artifact(artifact_id)
        if not artifact:
            return None

        # Create new version
        new_artifact = artifact.model_copy(deep=True)
        new_artifact.content = content
        new_artifact.checksum = hashlib.sha256(content.encode()).hexdigest()
        new_artifact.file_size = len(content.encode())
        new_artifact.updated_at = datetime.utcnow()
        new_artifact.version = self._increment_version(artifact.version)

        # Update version history
        new_artifact.version_history.append(
            {
                "version": artifact.version,
                "timestamp": artifact.updated_at.isoformat(),
                "changes": kwargs.get("changes", "Content updated"),
            }
        )

        # Update properties
        for key, value in kwargs.items():
            if hasattr(new_artifact, key):
                setattr(new_artifact, key, value)

        # Store updated artifact
        self.artifacts[artifact_id] = new_artifact

        # Update metadata
        await self._update_metadata(new_artifact)

        # Save to file system
        await self._save_artifact_to_file(new_artifact)

        return new_artifact

    async def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.

        Args:
            artifact_id: The artifact ID to delete

        Returns:
            True if deleted, False if not found
        """
        artifact = await self.get_artifact(artifact_id)
        if not artifact:
            return False

        # Remove from storage
        if artifact_id in self.artifacts:
            del self.artifacts[artifact_id]

        if artifact.id in self.metadata:
            del self.metadata[artifact.id]

        # Remove file
        file_path = self.storage_path / f"{artifact_id}.json"
        if file_path.exists():
            file_path.unlink()

        return True

    async def list_artifacts(
        self,
        project_id: Optional[UUID] = None,
        artifact_type: Optional[ArtifactType] = None,
        phase: Optional[str] = None,
    ) -> List[Artifact]:
        """
        List artifacts with optional filtering.

        Args:
            project_id: Filter by project ID
            artifact_type: Filter by artifact type
            phase: Filter by workflow phase

        Returns:
            List of matching artifacts
        """
        artifacts = list(self.artifacts.values())

        if project_id:
            artifacts = [a for a in artifacts if a.project_id == project_id]

        if artifact_type:
            artifacts = [a for a in artifacts if a.artifact_type == artifact_type]

        if phase:
            artifacts = [a for a in artifacts if a.phase == phase]

        return artifacts

    async def get_artifact_relationships(
        self, artifact_id: str
    ) -> Dict[str, List[str]]:
        """
        Get relationships for an artifact.

        Args:
            artifact_id: The artifact ID

        Returns:
            Dictionary of relationship types and related artifact IDs
        """
        artifact = await self.get_artifact(artifact_id)
        if not artifact:
            return {}

        return {
            "dependencies": artifact.dependencies,
            "related": artifact.related_artifacts,
            "superseded_by": [artifact.superseded_by] if artifact.superseded_by else [],
            "supersedes": artifact.supersedes,
        }

    async def add_artifact_relationship(
        self, artifact_id: str, related_artifact_id: str, relationship_type: str
    ) -> bool:
        """
        Add a relationship between artifacts.

        Args:
            artifact_id: Source artifact ID
            related_artifact_id: Related artifact ID
            relationship_type: Type of relationship

        Returns:
            True if relationship added, False otherwise
        """
        artifact = await self.get_artifact(artifact_id)
        related_artifact = await self.get_artifact(related_artifact_id)

        if not artifact or not related_artifact:
            return False

        if relationship_type == "dependency":
            if related_artifact_id not in artifact.dependencies:
                artifact.dependencies.append(related_artifact_id)
        elif relationship_type == "related":
            if related_artifact_id not in artifact.related_artifacts:
                artifact.related_artifacts.append(related_artifact_id)
        elif relationship_type == "supersedes":
            artifact.supersedes.append(related_artifact_id)
            related_artifact.superseded_by = artifact_id
        else:
            return False

        # Update artifacts
        self.artifacts[artifact_id] = artifact
        self.artifacts[related_artifact_id] = related_artifact

        return True

    async def _create_metadata(self, artifact: Artifact) -> ArtifactMetadata:
        """Create metadata for an artifact."""
        metadata = ArtifactMetadata(
            id=uuid4(),
            name=f"Metadata for {artifact.artifact_name}",
            description=f"Metadata for artifact {artifact.artifact_id}",
            status="active",
            artifact_id=artifact.id,
            metadata_type="artifact_metadata",
            content_type=self._determine_content_type(artifact),
            language=self._determine_language(artifact),
            framework=self._determine_framework(artifact),
        )

        return metadata

    async def _update_metadata(self, artifact: Artifact) -> None:
        """Update metadata for an artifact."""
        if artifact.id in self.metadata:
            metadata = self.metadata[artifact.id]
            metadata.usage_count += 1
            metadata.last_accessed = datetime.utcnow()
            metadata.access_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "updated",
                }
            )

    async def _save_artifact_to_file(self, artifact: Artifact) -> None:
        """Save artifact to file system."""
        file_path = self.storage_path / f"{artifact.artifact_id}.json"

        # Prepare data for serialization
        data = artifact.model_dump()
        data["created_at"] = data["created_at"].isoformat()
        data["updated_at"] = data["updated_at"].isoformat()

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        # Update file path
        artifact.file_path = str(file_path)

    def _determine_content_type(self, artifact: Artifact) -> str:
        """Determine content type based on artifact type."""
        content_type_map = {
            ArtifactType.DOCUMENT: "text/markdown",
            ArtifactType.CODE: "text/plain",
            ArtifactType.SPECIFICATION: "application/json",
            ArtifactType.DIAGRAM: "image/svg+xml",
            ArtifactType.TEST: "text/plain",
            ArtifactType.CONFIGURATION: "application/json",
            ArtifactType.DATA: "application/json",
            ArtifactType.REPORT: "text/markdown",
            ArtifactType.TEMPLATE: "text/plain",
            ArtifactType.OTHER: "text/plain",
        }

        return content_type_map.get(artifact.artifact_type, "text/plain")

    def _determine_language(self, artifact: Artifact) -> Optional[str]:
        """Determine programming language based on artifact content."""
        if artifact.artifact_type != ArtifactType.CODE:
            return None

        content = artifact.content or ""

        if "def " in content and "import " in content:
            return "python"
        elif "function " in content and "const " in content:
            return "javascript"
        elif "public class" in content and "public static void main" in content:
            return "java"
        elif "package main" in content and "func main" in content:
            return "go"
        else:
            return None

    def _determine_framework(self, artifact: Artifact) -> Optional[str]:
        """Determine framework based on artifact content."""
        if artifact.artifact_type != ArtifactType.CODE:
            return None

        content = artifact.content or ""

        if "from fastapi import" in content:
            return "fastapi"
        elif "from flask import" in content:
            return "flask"
        elif "import express" in content:
            return "express"
        elif "from django" in content:
            return "django"
        else:
            return None

    def _increment_version(self, version: str) -> str:
        """Increment version string."""
        try:
            parts = version.split(".")
            if len(parts) >= 3:
                major, minor, patch = parts[:3]
                patch_num = int(patch) + 1
                return f"{major}.{minor}.{patch_num}"
            else:
                return f"{version}.1"
        except (ValueError, IndexError):
            return f"{version}.1"
