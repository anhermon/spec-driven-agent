"""
Spec-Driven Context Engine for managing rich context with symbolic mechanisms.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import ValidationError

from ..models.context import (
    SpecDrivenContext,
    ContextUpdate,
    SymbolicData,
    SymbolicReference,
    ContextConsistencyValidator,
)
from ..models.project import Project
from .consistency_validator import ContextConsistencyValidator as ConsistencyValidator
from .symbolic_engine import SpecSymbolicEngine


class ContextInconsistencyError(Exception):
    """Raised when context updates would create inconsistent state."""
    
    def __init__(self, message: str, inconsistencies: Optional[List[str]] = None):
        super().__init__(message)
        self.inconsistencies = inconsistencies or []


class SpecDrivenContextEngine:
    """
    Core context engine for spec-driven development with consistency validation.
    
    Manages rich context with symbolic mechanisms, ensuring consistency
    across all context updates and providing atomic operations.
    """
    
    def __init__(self):
        """Initialize the context engine."""
        self.context_lock = asyncio.Lock()
        self.consistency_validator = ConsistencyValidator()
        self.symbolic_engine = SpecSymbolicEngine()
        self.contexts: Dict[UUID, SpecDrivenContext] = {}
        self.update_history: Dict[UUID, List[ContextUpdate]] = {}
        
    async def create_context(self, project: Project) -> SpecDrivenContext:
        """
        Create a new spec-driven context for a project.
        
        Args:
            project: The project to create context for
            
        Returns:
            The created context
        """
        context_id = uuid4()
        
        context = SpecDrivenContext(
            id=context_id,
            name=f"Context for {project.name}",
            description=f"Spec-driven context for project {project.name}",
            status="active",
            project_id=project.id,
            read_access=[project.id],  # Project has read access
            write_access=[project.id],  # Project has write access
        )
        
        # Initialize symbolic data for the project
        await self._initialize_symbolic_data(context, project)
        
        # Store context
        self.contexts[context_id] = context
        self.update_history[context_id] = []
        
        return context
    
    async def update_context(
        self, 
        context_id: UUID, 
        updates: List[ContextUpdate]
    ) -> None:
        """
        Update context with new information and consistency validation.
        
        Args:
            context_id: The context to update
            updates: List of updates to apply
            
        Raises:
            ContextInconsistencyError: If updates would create inconsistent state
        """
        async with self.context_lock:
            # Get current context
            context = await self.get_context(context_id)
            if not context:
                raise ValueError(f"Context {context_id} not found")
            
            # Apply updates atomically
            updated_context = await self._apply_updates(context, updates)
            
            # Validate consistency
            if not await self.consistency_validator.is_consistent(updated_context):
                inconsistencies = await self.consistency_validator.find_inconsistencies(updated_context)
                raise ContextInconsistencyError(
                    "Updates would create inconsistent state",
                    inconsistencies
                )
            
            # Commit changes atomically
            await self._save_context(context_id, updated_context)
            
            # Update history
            for update in updates:
                update.processed = True
                update.processed_at = datetime.utcnow()
                self.update_history[context_id].append(update)
            
            # Notify agents of context changes
            await self._notify_agents_of_context_update(context_id, updates)
    
    async def retrieve_context(self, context_id: UUID) -> Optional[SpecDrivenContext]:
        """
        Retrieve context by ID.
        
        Args:
            context_id: The context ID to retrieve
            
        Returns:
            The context if found, None otherwise
        """
        return self.contexts.get(context_id)
    
    async def get_context(self, context_id: UUID) -> Optional[SpecDrivenContext]:
        """
        Get context by ID (alias for retrieve_context).
        
        Args:
            context_id: The context ID to retrieve
            
        Returns:
            The context if found, None otherwise
        """
        return await self.retrieve_context(context_id)
    
    async def create_symbolic_representation(self, data: Any) -> SymbolicData:
        """
        Create symbolic representation of data.
        
        Args:
            data: The data to create symbolic representation for
            
        Returns:
            The symbolic data representation
        """
        return await self.symbolic_engine.create_symbolic_representation(data)
    
    async def resolve_symbolic_reference(self, reference: SymbolicReference) -> Any:
        """
        Resolve symbolic reference to concrete data.
        
        Args:
            reference: The symbolic reference to resolve
            
        Returns:
            The resolved concrete data
        """
        return await self.symbolic_engine.resolve_symbolic_reference(reference)
    
    async def maintain_symbolic_consistency(self, context: SpecDrivenContext) -> None:
        """
        Maintain consistency of symbolic representations.
        
        Args:
            context: The context to maintain consistency for
        """
        # Validate all symbolic references are consistent
        inconsistencies = await self.consistency_validator.find_inconsistencies(context)
        if inconsistencies:
            await self._resolve_inconsistencies(context, inconsistencies)
    
    async def apply_cognitive_tool(self, tool: Any, input_data: Any) -> Any:
        """
        Apply a cognitive tool to input data.
        
        Args:
            tool: The cognitive tool to apply
            input_data: The input data
            
        Returns:
            The result of applying the tool
        """
        return await self.symbolic_engine.apply_cognitive_tool(tool, input_data)
    
    async def chain_cognitive_tools(self, tools: List[Any], input_data: Any) -> Any:
        """
        Chain multiple cognitive tools together.
        
        Args:
            tools: List of cognitive tools to chain
            input_data: The input data
            
        Returns:
            The result of chaining the tools
        """
        return await self.symbolic_engine.chain_cognitive_tools(tools, input_data)
    
    async def _initialize_symbolic_data(self, context: SpecDrivenContext, project: Project) -> None:
        """Initialize symbolic data for a new context."""
        # Create symbolic representation of project requirements
        requirements_symbolic = await self.create_symbolic_representation({
            "name": project.name,
            "description": project.description,
            "stakeholders": project.stakeholders,
            "technical_constraints": project.technical_constraints,
        })
        
        context.symbolic_data["project_requirements"] = requirements_symbolic
        
        # Create symbolic references
        context.symbolic_references["requirements_ref"] = SymbolicReference(
            reference_id="requirements_ref",
            reference_type="project_requirements",
            symbolic_name="Project Requirements",
            symbolic_type="requirements",
            target_id=project.id,
        )
    
    async def _apply_updates(self, context: SpecDrivenContext, updates: List[ContextUpdate]) -> SpecDrivenContext:
        """Apply updates to context."""
        updated_context = context.model_copy(deep=True)
        
        for update in updates:
            # Apply update based on type
            if update.update_type == "requirements":
                updated_context.requirements.update(update.update_data)
            elif update.update_type == "specifications":
                updated_context.specifications.update(update.update_data)
            elif update.update_type == "architecture":
                updated_context.architecture.update(update.update_data)
            elif update.update_type == "implementation":
                updated_context.implementation.update(update.update_data)
            elif update.update_type == "symbolic_data":
                updated_context.symbolic_data.update(update.update_data)
            elif update.update_type == "symbolic_references":
                updated_context.symbolic_references.update(update.update_data)
            
            # Update metadata
            updated_context.updated_at = datetime.utcnow()
            updated_context.version += 1
            updated_context.update_history.append(update.id)
        
        return updated_context
    
    async def _save_context(self, context_id: UUID, context: SpecDrivenContext) -> None:
        """Save context to storage."""
        self.contexts[context_id] = context
    
    async def _notify_agents_of_context_update(self, context_id: UUID, updates: List[ContextUpdate]) -> None:
        """Notify agents of context updates."""
        # This would integrate with A2A SDK to notify relevant agents
        # For now, just log the notification
        for update in updates:
            print(f"Context {context_id} updated by {update.source_type}: {update.update_type}")
    
    async def _resolve_inconsistencies(self, context: SpecDrivenContext, inconsistencies: List[str]) -> None:
        """Resolve inconsistencies in context."""
        # This would implement logic to automatically resolve inconsistencies
        # For now, just log them
        print(f"Resolving inconsistencies in context {context.id}: {inconsistencies}")
        
        # Update context consistency status
        context.consistency_status = "resolving"
        context.consistency_errors = inconsistencies
        context.last_consistency_check = datetime.utcnow() 