"""
Context Consistency Validator for ensuring context consistency across updates.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..models.context import SpecDrivenContext, SymbolicData, SymbolicReference


class ContextConsistencyValidator:
    """
    Validates consistency of spec-driven context across updates.
    
    Ensures that context updates maintain consistency and don't create
    conflicting or invalid states.
    """
    
    def __init__(self):
        """Initialize the consistency validator."""
        self.validation_rules = self._initialize_validation_rules()
    
    async def is_consistent(self, context: SpecDrivenContext) -> bool:
        """
        Check if context is consistent.
        
        Args:
            context: The context to validate
            
        Returns:
            True if consistent, False otherwise
        """
        inconsistencies = await self.find_inconsistencies(context)
        return len(inconsistencies) == 0
    
    async def find_inconsistencies(self, context: SpecDrivenContext) -> List[str]:
        """
        Find inconsistencies in context.
        
        Args:
            context: The context to check
            
        Returns:
            List of inconsistency descriptions
        """
        inconsistencies = []
        
        # Check symbolic data consistency
        symbolic_inconsistencies = await self._check_symbolic_data_consistency(context)
        inconsistencies.extend(symbolic_inconsistencies)
        
        # Check symbolic references consistency
        reference_inconsistencies = await self._check_symbolic_references_consistency(context)
        inconsistencies.extend(reference_inconsistencies)
        
        # Check cross-reference consistency
        cross_ref_inconsistencies = await self._check_cross_reference_consistency(context)
        inconsistencies.extend(cross_ref_inconsistencies)
        
        # Check data integrity
        integrity_inconsistencies = await self._check_data_integrity(context)
        inconsistencies.extend(integrity_inconsistencies)
        
        # Check version consistency
        version_inconsistencies = await self._check_version_consistency(context)
        inconsistencies.extend(version_inconsistencies)
        
        return inconsistencies
    
    async def validate_update(
        self, 
        context: SpecDrivenContext, 
        updates: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Validate potential updates to context.
        
        Args:
            context: Current context
            updates: Proposed updates
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Create a copy of context with updates applied
        test_context = context.model_copy(deep=True)
        
        # Apply updates to test context
        for update in updates:
            await self._apply_test_update(test_context, update)
        
        # Check consistency of updated context
        inconsistencies = await self.find_inconsistencies(test_context)
        errors.extend(inconsistencies)
        
        return errors
    
    async def _check_symbolic_data_consistency(self, context: SpecDrivenContext) -> List[str]:
        """Check consistency of symbolic data."""
        inconsistencies = []
        
        for symbolic_id, symbolic_data in context.symbolic_data.items():
            # Check if symbolic data has valid structure
            if not symbolic_data.symbolic_name:
                inconsistencies.append(f"Symbolic data {symbolic_id} missing name")
            
            # Check if symbolic data has valid type
            if not symbolic_data.symbolic_type:
                inconsistencies.append(f"Symbolic data {symbolic_id} missing type")
            
            # Check parent-child relationships
            if symbolic_data.parent_symbolic_id:
                if symbolic_data.parent_symbolic_id not in context.symbolic_data:
                    inconsistencies.append(
                        f"Symbolic data {symbolic_id} references non-existent parent {symbolic_data.parent_symbolic_id}"
                    )
            
            # Check child relationships
            for child_id in symbolic_data.child_symbolic_ids:
                if child_id not in context.symbolic_data:
                    inconsistencies.append(
                        f"Symbolic data {symbolic_id} references non-existent child {child_id}"
                    )
        
        return inconsistencies
    
    async def _check_symbolic_references_consistency(self, context: SpecDrivenContext) -> List[str]:
        """Check consistency of symbolic references."""
        inconsistencies = []
        
        for ref_id, reference in context.symbolic_references.items():
            # Check if reference has valid structure
            if not reference.symbolic_name:
                inconsistencies.append(f"Symbolic reference {ref_id} missing name")
            
            # Check if reference has valid type
            if not reference.reference_type:
                inconsistencies.append(f"Symbolic reference {ref_id} missing type")
            
            # Check if resolved references point to valid targets
            if reference.resolved and reference.target_id:
                # This would check if target_id exists in the system
                # For now, just validate the structure
                pass
        
        return inconsistencies
    
    async def _check_cross_reference_consistency(self, context: SpecDrivenContext) -> List[str]:
        """Check consistency of cross-references between symbolic data and references."""
        inconsistencies = []
        
        # Check that all symbolic references have corresponding symbolic data
        for ref_id, reference in context.symbolic_references.items():
            if reference.symbolic_name not in context.symbolic_data:
                inconsistencies.append(
                    f"Symbolic reference {ref_id} references non-existent symbolic data {reference.symbolic_name}"
                )
        
        # Check that symbolic data references are valid
        for symbolic_id, symbolic_data in context.symbolic_data.items():
            for related_id in symbolic_data.related_symbolic_ids:
                if related_id not in context.symbolic_data:
                    inconsistencies.append(
                        f"Symbolic data {symbolic_id} references non-existent related data {related_id}"
                    )
        
        return inconsistencies
    
    async def _check_data_integrity(self, context: SpecDrivenContext) -> List[str]:
        """Check data integrity of context."""
        inconsistencies = []
        
        # Check that required fields are present
        if not context.project_id:
            inconsistencies.append("Context missing project_id")
        
        # Check that context type is valid
        if context.context_type not in ["spec_driven", "legacy", "migrated"]:
            inconsistencies.append(f"Invalid context type: {context.context_type}")
        
        # Check that version is positive
        if context.version < 1:
            inconsistencies.append(f"Invalid version: {context.version}")
        
        # Check that timestamps are valid
        if context.created_at > context.updated_at:
            inconsistencies.append("Created timestamp is after updated timestamp")
        
        return inconsistencies
    
    async def _check_version_consistency(self, context: SpecDrivenContext) -> List[str]:
        """Check version consistency of context."""
        inconsistencies = []
        
        # Check that version history matches current version
        if len(context.version_history) != context.version - 1:
            inconsistencies.append(
                f"Version history length ({len(context.version_history)}) "
                f"doesn't match version ({context.version})"
            )
        
        # Check that update history is consistent
        if len(context.update_history) != len(context.version_history):
            inconsistencies.append(
                f"Update history length ({len(context.update_history)}) "
                f"doesn't match version history length ({len(context.version_history)})"
            )
        
        return inconsistencies
    
    async def _apply_test_update(self, context: SpecDrivenContext, update: Dict[str, Any]) -> None:
        """Apply a test update to context for validation."""
        update_type = update.get("type")
        update_data = update.get("data", {})
        
        if update_type == "requirements":
            context.requirements.update(update_data)
        elif update_type == "specifications":
            context.specifications.update(update_data)
        elif update_type == "architecture":
            context.architecture.update(update_data)
        elif update_type == "implementation":
            context.implementation.update(update_data)
        elif update_type == "symbolic_data":
            context.symbolic_data.update(update_data)
        elif update_type == "symbolic_references":
            context.symbolic_references.update(update_data)
        
        # Update metadata
        context.updated_at = datetime.utcnow()
        context.version += 1
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules."""
        return {
            "symbolic_data": {
                "required_fields": ["symbolic_name", "symbolic_type"],
                "valid_types": ["requirements", "specifications", "architecture", "implementation"],
            },
            "symbolic_references": {
                "required_fields": ["reference_id", "reference_type", "symbolic_name"],
                "valid_types": ["api_spec", "requirement", "architecture", "implementation"],
            },
            "context": {
                "required_fields": ["project_id", "context_type"],
                "valid_types": ["spec_driven", "legacy", "migrated"],
            },
        } 