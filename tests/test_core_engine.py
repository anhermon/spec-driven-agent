"""
Tests for core engine components.
"""

import pytest
from uuid import uuid4

from spec_driven_agent.core import SpecDrivenContextEngine, SpecDrivenWorkflowOrchestrator
from spec_driven_agent.models.project import Project, ProjectStatus
from spec_driven_agent.models.context import SpecDrivenContext, ContextUpdate
from spec_driven_agent.models.workflow import WorkflowPhase, WorkflowStatus


class TestSpecDrivenContextEngine:
    """Test the Spec-Driven Context Engine."""
    
    @pytest.fixture
    def context_engine(self):
        """Create a context engine instance."""
        return SpecDrivenContextEngine()
    
    @pytest.fixture
    def sample_project(self):
        """Create a sample project."""
        return Project(
            id=uuid4(),
            name="Test Project",
            slug="test-project",
            description="A test project for testing",
            status=ProjectStatus.DRAFT,
        )
    
    @pytest.mark.asyncio
    async def test_create_context(self, context_engine, sample_project):
        """Test context creation."""
        context = await context_engine.create_context(sample_project)
        
        assert context is not None
        assert context.project_id == sample_project.id
        assert context.context_type == "spec_driven"
        assert context.status == "active"
        assert len(context.symbolic_data) > 0
        assert len(context.symbolic_references) > 0
    
    @pytest.mark.asyncio
    async def test_retrieve_context(self, context_engine, sample_project):
        """Test context retrieval."""
        # Create context
        created_context = await context_engine.create_context(sample_project)
        
        # Retrieve context
        retrieved_context = await context_engine.retrieve_context(created_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.id == created_context.id
        assert retrieved_context.project_id == sample_project.id
    
    @pytest.mark.asyncio
    async def test_update_context(self, context_engine, sample_project):
        """Test context updates."""
        # Create context
        context = await context_engine.create_context(sample_project)
        
        # Create update
        update = ContextUpdate(
            id=uuid4(),
            name="Test Update",
            description="A test context update",
            status="pending",
            context_id=context.id,
            update_type="requirements",
            update_data={"new_requirement": "Test requirement"},
            source_type="test",
        )
        
        # Apply update
        await context_engine.update_context(context.id, [update])
        
        # Verify update
        updated_context = await context_engine.retrieve_context(context.id)
        assert updated_context is not None
        assert updated_context.version > context.version
        assert "new_requirement" in updated_context.requirements
    
    @pytest.mark.asyncio
    async def test_create_symbolic_representation(self, context_engine):
        """Test symbolic representation creation."""
        test_data = {
            "name": "Test API",
            "version": "1.0.0",
            "endpoints": ["/users", "/posts"],
        }
        
        symbolic_data = await context_engine.create_symbolic_representation(test_data)
        
        assert symbolic_data is not None
        assert symbolic_data.symbolic_type == "api_specification"
        assert symbolic_data.symbolic_name is not None
        assert symbolic_data.concrete_data == test_data


class TestSpecDrivenWorkflowOrchestrator:
    """Test the Spec-Driven Workflow Orchestrator."""
    
    @pytest.fixture
    def workflow_orchestrator(self):
        """Create a workflow orchestrator instance."""
        return SpecDrivenWorkflowOrchestrator()
    
    @pytest.fixture
    def sample_project(self):
        """Create a sample project."""
        return Project(
            id=uuid4(),
            name="Test Project",
            slug="test-project",
            description="A test project for testing",
            status=ProjectStatus.DRAFT,
        )
    
    @pytest.mark.asyncio
    async def test_start_workflow(self, workflow_orchestrator, sample_project):
        """Test workflow start."""
        workflow = await workflow_orchestrator.start_workflow(sample_project)
        
        assert workflow is not None
        assert workflow.project_id == sample_project.id
        assert workflow.workflow_type == "spec_driven"
        assert workflow.current_phase == WorkflowPhase.DISCOVERY
        assert workflow.status == WorkflowStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_transition_workflow(self, workflow_orchestrator, sample_project):
        """Test workflow phase transitions."""
        # Start workflow
        workflow = await workflow_orchestrator.start_workflow(sample_project)
        
        # Transition to planning phase
        transitioned_workflow = await workflow_orchestrator.transition_to_phase(
            workflow.id, WorkflowPhase.PLANNING
        )
        
        assert transitioned_workflow is not None
        assert transitioned_workflow.current_phase == WorkflowPhase.PLANNING
        assert WorkflowPhase.DISCOVERY in transitioned_workflow.completed_phases
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, workflow_orchestrator, sample_project):
        """Test workflow status retrieval."""
        # Start workflow
        workflow = await workflow_orchestrator.start_workflow(sample_project)
        
        # Get status
        status = await workflow_orchestrator.get_workflow_status(workflow.id)
        
        assert status is not None
        assert status["workflow_id"] == str(workflow.id)
        assert status["current_phase"] == WorkflowPhase.DISCOVERY
        assert status["status"] == WorkflowStatus.ACTIVE


class TestIntegration:
    """Integration tests for core components."""
    
    @pytest.mark.asyncio
    async def test_project_workflow_integration(self):
        """Test integration between project, context, and workflow."""
        # Create components
        context_engine = SpecDrivenContextEngine()
        workflow_orchestrator = SpecDrivenWorkflowOrchestrator()
        
        # Create project
        project = Project(
            id=uuid4(),
            name="Integration Test Project",
            slug="integration-test",
            description="A project for integration testing",
            status=ProjectStatus.DRAFT,
        )
        
        # Create context
        context = await context_engine.create_context(project)
        
        # Start workflow
        workflow = await workflow_orchestrator.start_workflow(project)
        
        # Verify integration
        assert context.project_id == project.id
        assert workflow.project_id == project.id
        assert context.id is not None
        assert workflow.id is not None
        
        # Test workflow transition
        transitioned_workflow = await workflow_orchestrator.transition_to_phase(
            workflow.id, WorkflowPhase.PLANNING
        )
        
        assert transitioned_workflow.current_phase == WorkflowPhase.PLANNING 