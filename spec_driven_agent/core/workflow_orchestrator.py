"""
Workflow orchestrator for the spec-driven agent workflow system.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ..models.project import Project
from ..models.workflow import (
    WorkflowInstance,
    WorkflowPhase,
    WorkflowState,
    WorkflowStatus,
    WorkflowTransition,
)
from .context_engine import SpecDrivenContextEngine


class WorkflowOrchestrationError(Exception):
    """Raised when workflow orchestration fails."""

    def __init__(self, message: str, workflow_id: Optional[UUID] = None):
        super().__init__(message)
        self.workflow_id = workflow_id


class SpecDrivenWorkflowOrchestrator:
    """
    Orchestrates spec-driven workflows with phase management and agent coordination.

    Manages workflow phases, state transitions, agent assignments, and ensures
    proper dependency validation and user visibility throughout the process.
    """

    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.workflow_lock = asyncio.Lock()
        self.context_engine = SpecDrivenContextEngine()
        self.workflows: Dict[UUID, WorkflowInstance] = {}
        self.workflow_states: Dict[UUID, WorkflowState] = {}
        self.transition_history: Dict[UUID, List[WorkflowTransition]] = {}

        # Phase dependencies and validation rules
        self.phase_dependencies = self._initialize_phase_dependencies()
        self.phase_validators = self._initialize_phase_validators()

    async def start_workflow(self, project: Project) -> WorkflowInstance:
        """
        Start a new spec-driven workflow for a project.

        Args:
            project: The project to start workflow for

        Returns:
            The created workflow instance
        """
        async with self.workflow_lock:
            # Create workflow instance
            workflow_id = uuid4()

            workflow = WorkflowInstance(
                id=workflow_id,
                name=f"Workflow for {project.name}",
                description=f"Spec-driven workflow for project {project.name}",
                status=WorkflowStatus.ACTIVE,
                project_id=project.id,
                workflow_type="spec_driven",
                current_phase=WorkflowPhase.DISCOVERY,
                started_at=datetime.now(timezone.utc),
            )

            # Create initial workflow state
            state = WorkflowState(
                id=uuid4(),
                name="Initial State",
                description="Initial workflow state",
                status="active",
                workflow_id=workflow_id,
                current_phase=WorkflowPhase.DISCOVERY,
                phase_started_at=datetime.now(timezone.utc),
            )

            # Store workflow and state
            self.workflows[workflow_id] = workflow
            self.workflow_states[workflow_id] = state
            self.transition_history[workflow_id] = []

            # Update workflow with state reference
            workflow.state_id = state.id
            workflow.state_history.append(state.id)

            # Initialize context if not already created
            if not project.context_id:
                context = await self.context_engine.create_context(project)
                workflow.context_id = context.id
                project.context_id = context.id

            return workflow

    async def transition_to_phase(
        self,
        workflow_id: UUID,
        target_phase: WorkflowPhase,
        trigger_reason: str = "User request",
    ) -> WorkflowInstance:
        """
        Transition workflow to a new phase with validation.

        Args:
            workflow_id: The workflow to transition
            target_phase: The target phase
            trigger_reason: Reason for the transition

        Returns:
            The updated workflow instance

        Raises:
            WorkflowOrchestrationError: If transition is invalid
        """
        async with self.workflow_lock:
            # Get current workflow
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                raise WorkflowOrchestrationError(
                    f"Workflow {workflow_id} not found", workflow_id
                )

            # Validate transition
            if not await self._validate_phase_transition(workflow, target_phase):
                raise WorkflowOrchestrationError(
                    f"Invalid transition from {workflow.current_phase} to {target_phase}",
                    workflow_id,
                )

            # Create transition record
            transition = WorkflowTransition(
                id=uuid4(),
                name=f"Transition to {target_phase}",
                description=f"Workflow transition to {target_phase}",
                status="active",
                workflow_id=workflow_id,
                from_phase=workflow.current_phase,
                to_phase=target_phase,
                triggered_by="system",
                trigger_reason=trigger_reason,
                dependencies_satisfied=True,
                validation_passed=True,
                transition_started_at=datetime.now(timezone.utc),
            )

            # Update workflow state
            current_state = self.workflow_states[workflow_id]
            current_state.current_phase = target_phase
            current_state.phase_completed_at = datetime.now(timezone.utc)

            # Create new state for target phase
            new_state = WorkflowState(
                id=uuid4(),
                name=f"State for {target_phase}",
                description=f"Workflow state for {target_phase} phase",
                status="active",
                workflow_id=workflow_id,
                current_phase=target_phase,
                phase_started_at=datetime.now(timezone.utc),
            )

            # Update workflow
            previous_phase = workflow.current_phase
            workflow.current_phase = target_phase
            # Mark previous phase as completed
            workflow.completed_phases.append(previous_phase)
            workflow.phase_history.append(
                {
                    "from_phase": transition.from_phase,
                    "to_phase": transition.to_phase,
                    "timestamp": transition.transition_started_at.isoformat(),
                    "reason": transition.trigger_reason,
                }
            )
            workflow.state_id = new_state.id
            workflow.state_history.append(new_state.id)

            # Store new state and transition
            self.workflow_states[workflow_id] = new_state
            self.transition_history[workflow_id].append(transition)

            # Complete transition
            transition.transition_completed_at = datetime.now(timezone.utc)

            # Notify agents of phase change
            await self._notify_agents_of_phase_change(workflow_id, target_phase)

            return workflow

    async def get_workflow(self, workflow_id: UUID) -> Optional[WorkflowInstance]:
        """
        Get workflow by ID.

        Args:
            workflow_id: The workflow ID to retrieve

        Returns:
            The workflow instance if found, None otherwise
        """
        return self.workflows.get(workflow_id)

    async def get_workflow_status(self, workflow_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive workflow status.

        Args:
            workflow_id: The workflow ID to get status for

        Returns:
            Dictionary containing workflow status information
        """
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        state = self.workflow_states.get(workflow_id)

        return {
            "workflow_id": str(workflow_id),
            "project_id": str(workflow.project_id),
            "current_phase": workflow.current_phase,
            "status": workflow.status,
            "started_at": workflow.started_at.isoformat(),
            "phase_started_at": state.phase_started_at.isoformat() if state else None,
            "completed_phases": workflow.completed_phases,
            "total_phases": len(WorkflowPhase.__dict__)
            - 1,  # Exclude internal attributes
            "progress_percentage": self._calculate_progress(workflow),
        }

    async def assign_agent_to_workflow(
        self, workflow_id: UUID, agent_id: UUID, role: str
    ) -> None:
        """
        Assign an agent to a workflow with a specific role.

        Args:
            workflow_id: The workflow to assign agent to
            agent_id: The agent ID to assign
            role: The role for the agent
        """
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise WorkflowOrchestrationError(
                f"Workflow {workflow_id} not found", workflow_id
            )

        if agent_id not in workflow.assigned_agents:
            workflow.assigned_agents.append(agent_id)

        workflow.agent_roles[agent_id] = role

    async def get_workflow_dependencies(self, workflow_id: UUID) -> Dict[str, Any]:
        """
        Get workflow dependencies and validation status.

        Args:
            workflow_id: The workflow ID to get dependencies for

        Returns:
            Dictionary containing dependency information
        """
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        current_phase = workflow.current_phase
        dependencies = self.phase_dependencies.get(current_phase, [])

        return {
            "workflow_id": str(workflow_id),
            "current_phase": current_phase,
            "dependencies": dependencies,
            "satisfied_dependencies": [],  # This would be calculated
            "pending_dependencies": dependencies,  # This would be calculated
        }

    async def _validate_phase_transition(
        self, workflow: WorkflowInstance, target_phase: WorkflowPhase
    ) -> bool:
        """Validate if a phase transition is allowed."""
        current_phase = workflow.current_phase

        # Check if target phase is valid
        if target_phase not in WorkflowPhase.__dict__.values():
            return False

        # Check phase order (simplified validation)
        phase_order = [
            WorkflowPhase.DISCOVERY,
            WorkflowPhase.PLANNING,
            WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.DESIGN,
            WorkflowPhase.DEVELOPMENT,
            WorkflowPhase.TESTING,
            WorkflowPhase.DEPLOYMENT,
            WorkflowPhase.COMPLETED,
        ]

        try:
            current_index = phase_order.index(current_phase)
            target_index = phase_order.index(target_phase)

            # Allow forward transitions and staying in same phase
            return target_index >= current_index
        except ValueError:
            return False

    async def _notify_agents_of_phase_change(
        self, workflow_id: UUID, new_phase: WorkflowPhase
    ) -> None:
        """Notify agents of phase change."""
        # This would integrate with A2A SDK to notify relevant agents
        # For now, just log the notification
        print(f"Workflow {workflow_id} transitioned to phase: {new_phase}")

    def _calculate_progress(self, workflow: WorkflowInstance) -> float:
        """Calculate workflow progress percentage."""
        total_phases = 8  # Total number of phases
        completed_count = len(workflow.completed_phases)
        return (completed_count / total_phases) * 100

    def _initialize_phase_dependencies(self) -> Dict[WorkflowPhase, List[str]]:
        """Initialize phase dependencies."""
        return {
            WorkflowPhase.DISCOVERY: [],
            WorkflowPhase.PLANNING: ["discovery_complete"],
            WorkflowPhase.ARCHITECTURE: ["planning_complete"],
            WorkflowPhase.DESIGN: ["architecture_complete"],
            WorkflowPhase.DEVELOPMENT: ["design_complete"],
            WorkflowPhase.TESTING: ["development_complete"],
            WorkflowPhase.DEPLOYMENT: ["testing_complete"],
            WorkflowPhase.COMPLETED: ["deployment_complete"],
        }

    def _initialize_phase_validators(self) -> Dict[WorkflowPhase, Any]:
        """Initialize phase validators."""
        # This would contain validation functions for each phase
        return {
            WorkflowPhase.DISCOVERY: None,
            WorkflowPhase.PLANNING: None,
            WorkflowPhase.ARCHITECTURE: None,
            WorkflowPhase.DESIGN: None,
            WorkflowPhase.DEVELOPMENT: None,
            WorkflowPhase.TESTING: None,
            WorkflowPhase.DEPLOYMENT: None,
            WorkflowPhase.COMPLETED: None,
        }
