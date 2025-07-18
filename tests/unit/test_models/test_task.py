"""
Unit tests for Task model.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from pydantic import ValidationError

from spec_driven_agent.models.task import Task, TaskStatus


class TestTask:
    """Test Task model functionality."""

    def test_task_initialization(self):
        """Test basic task initialization."""
        task = Task(
            task_id="task-001",
            task_name="Test Task",
            task_type="requirements_gathering",
            description="A test task",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        assert task.task_id == "task-001"
        assert task.task_name == "Test Task"
        assert task.task_type == "requirements_gathering"
        assert task.description == "A test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == "medium"
        assert task.effort_estimate == 4.0
        assert task.phase == "discovery"

    def test_task_with_optional_fields(self):
        """Test task initialization with optional fields."""
        task = Task(
            task_id="task-002",
            task_name="Optional Fields Task",
            task_type="market_research",
            description="A task with optional fields",
            status=TaskStatus.IN_PROGRESS,
            priority="high",
            effort_estimate=8.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
            due_date=datetime.now() + timedelta(days=7),
            requirements=["requirement1", "requirement2"],
            acceptance_criteria=["criteria1", "criteria2"],
        )
        
        assert task.due_date is not None
        assert task.requirements == ["requirement1", "requirement2"]
        assert task.acceptance_criteria == ["criteria1", "criteria2"]

    def test_task_validation_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            Task()  # Missing all required fields

    def test_task_validation_missing_task_id(self):
        """Test validation of required task_id field."""
        with pytest.raises(ValidationError):
            Task(
                task_name="Test Task",
                task_type="requirements_gathering",
                description="A test task",
                status=TaskStatus.PENDING,
                priority="medium",
                effort_estimate=4.0,
                workflow_id=uuid4(),
                phase="discovery",
            )

    def test_task_validation_missing_workflow_id(self):
        """Test validation of required workflow_id field."""
        with pytest.raises(ValidationError):
            Task(
                task_id="task-003",
                task_name="Test Task",
                task_type="requirements_gathering",
                description="A test task",
                status=TaskStatus.PENDING,
                priority="medium",
                effort_estimate=4.0,
                phase="discovery",
            )

    def test_task_serialization(self):
        """Test task serialization to dict."""
        task = Task(
            task_id="task-006",
            task_name="Serialization Test Task",
            task_type="prd_creation",
            description="A task for testing serialization",
            status=TaskStatus.COMPLETED,
            priority="high",
            effort_estimate=12.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="planning",
        )
        
        task_dict = task.model_dump()
        
        assert task_dict["task_id"] == "task-006"
        assert task_dict["task_name"] == "Serialization Test Task"
        assert task_dict["task_type"] == "prd_creation"
        assert task_dict["status"] == "completed"
        assert task_dict["priority"] == "high"
        assert task_dict["effort_estimate"] == 12.0

    def test_task_deserialization(self):
        """Test task deserialization from dict."""
        task_data = {
            "task_id": "task-007",
            "task_name": "Deserialization Test Task",
            "task_type": "market_research",
            "description": "A task for testing deserialization",
            "status": "pending",
            "priority": "medium",
            "effort_estimate": 6.0,
            "assigned_agent_id": str(uuid4()),
            "workflow_id": str(uuid4()),
            "phase": "discovery",
            "requirements": ["req1"],
        }
        
        task = Task.model_validate(task_data)
        
        assert task.task_id == "task-007"
        assert task.task_name == "Deserialization Test Task"
        assert task.task_type == "market_research"
        assert task.status == TaskStatus.PENDING
        assert task.priority == "medium"
        assert task.effort_estimate == 6.0
        assert task.requirements == ["req1"]

    def test_task_status_transitions(self):
        """Test task status transition logic."""
        task = Task(
            task_id="task-008",
            task_name="Status Transition Task",
            task_type="requirements_gathering",
            description="A task for testing status transitions",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        # Test status updates
        task.status = TaskStatus.IN_PROGRESS
        assert task.status == TaskStatus.IN_PROGRESS
        
        task.status = TaskStatus.COMPLETED
        assert task.status == TaskStatus.COMPLETED

    def test_task_priority_values(self):
        """Test task priority values."""
        task = Task(
            task_id="task-009",
            task_name="Priority Test Task",
            task_type="requirements_gathering",
            description="A task for testing priorities",
            status=TaskStatus.PENDING,
            priority="high",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        assert task.priority == "high"
        
        task.priority = "low"
        assert task.priority == "low"
        
        task.priority = "critical"
        assert task.priority == "critical"

    def test_task_equality(self):
        """Test task equality comparison."""
        task1 = Task(
            task_id="task-012",
            task_name="Equality Test Task",
            task_type="requirements_gathering",
            description="A task for testing equality",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        task2 = Task(
            task_id="task-012",  # Same ID
            task_name="Different Name",
            task_type="market_research",  # Different type
            description="Different description",
            status=TaskStatus.COMPLETED,  # Different status
            priority="high",  # Different priority
            effort_estimate=8.0,  # Different hours
            assigned_agent_id=uuid4(),  # Different agent
            workflow_id=uuid4(),  # Different workflow
            phase="planning",  # Different phase
        )
        
        # Tasks with same ID should be equal
        assert task1.task_id == task2.task_id
        
        # Different ID should not be equal
        task3 = Task(
            task_id="task-013",  # Different ID
            task_name="Equality Test Task",
            task_type="requirements_gathering",
            description="A task for testing equality",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        assert task1.task_id != task3.task_id

    def test_task_str_representation(self):
        """Test task string representation."""
        task = Task(
            task_id="task-014",
            task_name="String Test Task",
            task_type="requirements_gathering",
            description="A task for testing string representation",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        str_repr = str(task)
        assert "String Test Task" in str_repr
        assert "task-014" in str_repr

    def test_task_repr_representation(self):
        """Test task repr representation."""
        task = Task(
            task_id="task-015",
            task_name="Repr Test Task",
            task_type="requirements_gathering",
            description="A task for testing repr representation",
            status=TaskStatus.PENDING,
            priority="medium",
            effort_estimate=4.0,
            assigned_agent_id=uuid4(),
            workflow_id=uuid4(),
            phase="discovery",
        )
        
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "task-015" in repr_str
        assert "Repr Test Task" in repr_str

    def test_task_status_enum_values(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled" 