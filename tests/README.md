# Testing Guide

This directory contains comprehensive tests for the spec-driven-agent project, including unit tests, integration tests, and test utilities.

## 📁 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests by module
│   ├── test_agents/               # Agent tests
│   │   ├── test_base_agent.py
│   │   ├── test_analyst_agent.py
│   │   ├── test_product_manager_agent.py
│   │   └── test_agent_manager.py
│   ├── test_models/               # Data model tests
│   │   ├── test_task.py
│   │   ├── test_agent.py
│   │   ├── test_artifact.py
│   │   ├── test_context.py
│   │   ├── test_project.py
│   │   ├── test_specification.py
│   │   └── test_workflow.py
│   ├── test_core/                 # Core engine tests
│   │   ├── test_context_engine.py
│   │   ├── test_workflow_orchestrator.py
│   │   ├── test_artifact_manager.py
│   │   ├── test_state_manager.py
│   │   ├── test_symbolic_engine.py
│   │   └── test_consistency_validator.py
│   └── test_cli/                  # CLI tests
│       └── test_main.py
├── integration/                   # Integration tests
│   ├── test_api_integration.py
│   ├── test_agent_workflow.py
│   └── test_end_to_end.py
├── fixtures/                      # Test data and fixtures
│   ├── sample_data.py
│   └── mock_responses.py
└── utils/                         # Test utilities
    └── test_helpers.py
```

## 🚀 Quick Start

### 1. Setup Testing Environment

```bash
# Run the setup script (recommended)
./scripts/setup_testing.sh

# Or manually:
pip install -r requirements.txt
pip install -e ".[dev]"
pre-commit install
```

### 2. Run Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run all integration tests
pytest tests/integration/ -v

# Run all tests with coverage
pytest --cov=spec_driven_agent --cov-report=html

# Run specific test file
pytest tests/unit/test_agents/test_base_agent.py -v

# Run tests matching a pattern
pytest -k "test_agent" -v
```

## 🧪 Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation:

- **Agent Tests**: Test agent functionality, task processing, and capabilities
- **Model Tests**: Test data validation, serialization, and business logic
- **Core Tests**: Test core engine components and workflows
- **CLI Tests**: Test command-line interface functionality

### Integration Tests

Integration tests verify that components work together correctly:

- **API Integration**: Test API endpoints and request/response handling
- **Agent Workflow**: Test multi-agent coordination and task flow
- **End-to-End**: Test complete user scenarios

### Test Utilities

- **TestDataFactory**: Factory for creating test data objects
- **AsyncTestCase**: Base class for async test cases
- **TestAssertions**: Custom assertions for common patterns
- **MockResponse**: Mock HTTP responses for testing

## 📊 Coverage Requirements

- **Unit Tests**: 90%+ coverage for core business logic
- **Integration Tests**: 70%+ coverage for API endpoints
- **Critical Paths**: 100% coverage for error handling

## 🔧 Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks on staged files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
```

### Quality Gates

- **Code Formatting**: Black and isort
- **Linting**: Flake8 with project-specific rules
- **Type Checking**: MyPy (optional in pre-commit)
- **Unit Tests**: All tests must pass
- **Coverage**: Minimum 80% coverage requirement
- **Security**: Bandit security checks

## 🎯 Writing Tests

### Test Naming Convention

```python
def test_component_functionality_description():
    """Test description of what is being tested."""
    # Test implementation
```

### Async Test Pattern

```python
@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality."""
    result = await some_async_function()
    assert result is not None
```

### Using Fixtures

```python
def test_with_fixture(sample_agent, sample_task):
    """Test using fixtures."""
    result = sample_agent.process_task(sample_task)
    assert result["status"] == "completed"
```

### Mocking

```python
@patch("module.function")
def test_with_mock(mock_function):
    """Test with mocked dependencies."""
    mock_function.return_value = "mocked_result"
    result = function_under_test()
    assert result == "mocked_result"
```

### Test Data Factory

```python
from tests.utils.test_helpers import TestDataFactory

def test_with_factory():
    """Test using the test data factory."""
    task = TestDataFactory.create_task(
        name="Custom Task",
        task_type=TaskType.REQUIREMENTS_GATHERING
    )
    assert task.name == "Custom Task"
```

## 🔍 Debugging Tests

### Verbose Output

```bash
pytest -v -s  # Verbose with print statements
pytest --tb=long  # Full traceback
pytest --tb=short  # Short traceback
```

### Debugging Specific Tests

```bash
# Run with debugger
pytest --pdb

# Run specific test with debugger
pytest test_file.py::test_function --pdb
```

### Coverage Analysis

```bash
# Generate HTML coverage report
pytest --cov=spec_driven_agent --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 📈 Performance Testing

### Execution Time

```python
from tests.utils.test_helpers import PerformanceTestMixin

class TestPerformance(PerformanceTestMixin):
    async def test_performance(self):
        """Test that function completes within time limit."""
        result, execution_time = await self.measure_execution_time(
            some_async_function(), max_seconds=5.0
        )
        assert execution_time < 5.0
```

### Memory Usage

```python
def test_memory_usage(self):
    """Test that function doesn't use excessive memory."""
    result = self.assert_memory_usage_acceptable(
        some_function, max_memory_mb=100.0
    )
```

## 🚨 Common Issues

### Import Errors

If you encounter import errors:

1. Ensure you're in the project root directory
2. Activate the virtual environment: `source .venv/bin/activate`
3. Install the package in development mode: `pip install -e .`

### Async Test Issues

For async test issues:

1. Use `@pytest.mark.asyncio` decorator
2. Ensure proper event loop setup in `conftest.py`
3. Use `await` for async function calls

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. Run `pre-commit run --all-files` to see all issues
2. Fix formatting issues: `black .` and `isort .`
3. Fix linting issues: `flake8 .`
4. Fix type issues: `mypy spec_driven_agent/`

## 📚 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests with clear sections
4. **Minimal Fixtures**: Keep fixtures focused and minimal
5. **Mock External Dependencies**: Don't rely on external services
6. **Test Edge Cases**: Include error conditions and edge cases
7. **Fast Tests**: Keep tests fast for quick feedback
8. **Clear Assertions**: Use specific, meaningful assertions

## 🔄 Continuous Integration

Tests are automatically run in CI/CD pipelines:

- **Pre-commit**: Runs on every commit
- **Pre-push**: Runs before pushing to remote
- **CI Pipeline**: Runs on pull requests and merges

## 📞 Getting Help

- Check the test output for specific error messages
- Review the test structure and naming conventions
- Consult the pytest documentation: https://docs.pytest.org/
- Check the pre-commit documentation: https://pre-commit.com/

---

**Happy Testing! 🎯** 