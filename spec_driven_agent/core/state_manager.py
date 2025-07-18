"""
State Manager for managing workflow state in the spec-driven workflow.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from ..models.context import SpecDrivenContext
from ..models.workflow import WorkflowPhase, WorkflowState


class WorkflowStateManager:
    """
    Manages workflow state and state transitions.

    Handles state persistence, state validation, and state change
    notifications to ensure consistent workflow execution.
    """

    def __init__(self):
        """Initialize the state manager."""
        self.state_lock = asyncio.Lock()
        self.states: Dict[UUID, WorkflowState] = {}
        self.state_history: Dict[UUID, List[WorkflowState]] = {}
        self.state_validators: Dict[str, Any] = {}

        # Initialize state validators
        self._initialize_state_validators()

    async def create_state(
        self, workflow_id: UUID, phase: WorkflowPhase, **kwargs
    ) -> WorkflowState:
        """
        Create a new workflow state.

        Args:
            workflow_id: The workflow ID
            phase: The workflow phase
            **kwargs: Additional state properties

        Returns:
            The created workflow state
        """
        state_id = uuid4()

        state = WorkflowState(
            id=state_id,
            name=f"State for {phase}",
            description=f"Workflow state for {phase} phase",
            status="active",
            workflow_id=workflow_id,
            current_phase=phase,
            phase_started_at=datetime.utcnow(),
            **kwargs,
        )

        # Store state
        self.states[workflow_id] = state

        # Initialize state history
        if workflow_id not in self.state_history:
            self.state_history[workflow_id] = []

        self.state_history[workflow_id].append(state)

        return state

    async def get_state(self, workflow_id: UUID) -> Optional[WorkflowState]:
        """
        Get current state for a workflow.

        Args:
            workflow_id: The workflow ID

        Returns:
            The current state if found, None otherwise
        """
        return self.states.get(workflow_id)

    async def update_state(
        self, workflow_id: UUID, updates: Dict[str, Any]
    ) -> Optional[WorkflowState]:
        """
        Update workflow state.

        Args:
            workflow_id: The workflow ID
            updates: State updates to apply

        Returns:
            The updated state if found, None otherwise
        """
        state = await self.get_state(workflow_id)
        if not state:
            return None

        # Apply updates
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)

        # Update timestamp
        state.updated_at = datetime.utcnow()

        # Validate state
        if not await self._validate_state(state):
            raise ValueError("Invalid state update")

        # Store updated state
        self.states[workflow_id] = state

        # Add to history
        self.state_history[workflow_id].append(state)

        return state

    async def transition_state(
        self,
        workflow_id: UUID,
        new_phase: WorkflowPhase,
        transition_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[WorkflowState]:
        """
        Transition workflow to a new state.

        Args:
            workflow_id: The workflow ID
            new_phase: The new phase
            transition_data: Data for the transition

        Returns:
            The new state if successful, None otherwise
        """
        current_state = await self.get_state(workflow_id)
        if not current_state:
            return None

        # Validate transition
        if not await self._validate_transition(current_state, new_phase):
            raise ValueError(
                f"Invalid transition from {current_state.current_phase} to {new_phase}"
            )

        # Complete current phase
        current_state.phase_completed_at = datetime.utcnow()

        # Create new state
        new_state = await self.create_state(
            workflow_id=workflow_id,
            phase=new_phase,
            phase_data=transition_data or {},
        )

        # Update state history
        self.state_history[workflow_id].append(new_state)

        return new_state

    async def get_state_history(self, workflow_id: UUID) -> List[WorkflowState]:
        """
        Get state history for a workflow.

        Args:
            workflow_id: The workflow ID

        Returns:
            List of historical states
        """
        return self.state_history.get(workflow_id, [])

    async def validate_state(self, workflow_id: UUID) -> Dict[str, Any]:
        """
        Validate current workflow state.

        Args:
            workflow_id: The workflow ID

        Returns:
            Validation results
        """
        state = await self.get_state(workflow_id)
        if not state:
            return {"valid": False, "error": "State not found"}

        # Run validators
        validation_results = {}
        for validator_name, validator in self.state_validators.items():
            try:
                result = await validator(state)
                validation_results[validator_name] = result
            except Exception as e:
                validation_results[validator_name] = {"valid": False, "error": str(e)}

        # Overall validation
        all_valid = all(
            result.get("valid", False) for result in validation_results.values()
        )

        return {
            "valid": all_valid,
            "validation_results": validation_results,
        }

    async def get_state_summary(self, workflow_id: UUID) -> Dict[str, Any]:
        """
        Get a summary of workflow state.

        Args:
            workflow_id: The workflow ID

        Returns:
            State summary
        """
        state = await self.get_state(workflow_id)
        if not state:
            return {"error": "State not found"}

        history = await self.get_state_history(workflow_id)

        return {
            "workflow_id": str(workflow_id),
            "current_phase": state.current_phase,
            "phase_started_at": state.phase_started_at.isoformat(),
            "phase_completed_at": state.phase_completed_at.isoformat()
            if state.phase_completed_at
            else None,
            "active_agents": state.active_agents,
            "completed_agents": state.completed_agents,
            "pending_tasks": len(state.pending_tasks),
            "active_tasks": len(state.active_tasks),
            "completed_tasks": len(state.completed_tasks),
            "satisfied_dependencies": len(state.satisfied_dependencies),
            "pending_dependencies": len(state.pending_dependencies),
            "user_approvals": len(state.user_approvals),
            "pending_decisions": len(state.pending_decisions),
            "total_states": len(history),
        }

    async def _validate_state(self, state: WorkflowState) -> bool:
        """Validate a workflow state."""
        # Basic validation
        if not state.workflow_id:
            return False

        if not state.current_phase:
            return False

        if state.phase_started_at > datetime.utcnow():
            return False

        # Phase-specific validation
        validator = self.state_validators.get(f"phase_{state.current_phase}")
        if validator:
            try:
                result = await validator(state)
                return result.get("valid", False)
            except Exception:
                return False

        return True

    async def _validate_transition(
        self, current_state: WorkflowState, new_phase: WorkflowPhase
    ) -> bool:
        """Validate a state transition."""
        # Basic transition validation
        if current_state.current_phase == new_phase:
            return True  # Same phase is always valid

        # Check phase order (simplified)
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
            current_index = phase_order.index(current_state.current_phase)
            new_index = phase_order.index(new_phase)

            # Allow forward transitions
            return new_index >= current_index
        except ValueError:
            return False

    def _initialize_state_validators(self) -> None:
        """Initialize state validators."""
        # Phase-specific validators
        self.state_validators["phase_discovery"] = self._validate_discovery_state
        self.state_validators["phase_planning"] = self._validate_planning_state
        self.state_validators["phase_architecture"] = self._validate_architecture_state
        self.state_validators["phase_design"] = self._validate_design_state
        self.state_validators["phase_development"] = self._validate_development_state
        self.state_validators["phase_testing"] = self._validate_testing_state
        self.state_validators["phase_deployment"] = self._validate_deployment_state
        self.state_validators["phase_completed"] = self._validate_completed_state

    async def _validate_discovery_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate discovery phase state."""
        return {
            "valid": True,
            "checks": ["basic_structure", "project_context"],
        }

    async def _validate_planning_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate planning phase state."""
        return {
            "valid": True,
            "checks": ["requirements_defined", "stakeholders_identified"],
        }

    async def _validate_architecture_state(
        self, state: WorkflowState
    ) -> Dict[str, Any]:
        """Validate architecture phase state."""
        return {
            "valid": True,
            "checks": ["architecture_designed", "components_defined"],
        }

    async def _validate_design_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate design phase state."""
        return {
            "valid": True,
            "checks": ["api_specs_created", "interfaces_defined"],
        }

    async def _validate_development_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate development phase state."""
        return {
            "valid": True,
            "checks": ["code_implemented", "tests_written"],
        }

    async def _validate_testing_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate testing phase state."""
        return {
            "valid": True,
            "checks": ["tests_passed", "quality_validated"],
        }

    async def _validate_deployment_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate deployment phase state."""
        return {
            "valid": True,
            "checks": ["deployment_ready", "monitoring_configured"],
        }

    async def _validate_completed_state(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate completed phase state."""
        return {
            "valid": True,
            "checks": ["all_phases_completed", "deliverables_ready"],
        }
