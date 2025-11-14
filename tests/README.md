# Tests

Comprehensive test suite for Council of Mine MCP Server.

## Structure

```
tests/
├── conftest.py           # Pytest configuration and shared fixtures
├── unit/                 # Unit tests for individual components
│   └── test_security.py  # Security validation tests
└── integration/          # Integration tests (future)
    └── (coming soon)
```

## Running Tests

### Run All Tests
```bash
# Using pytest (recommended)
PYTHONPATH=. pytest tests/

# Or with uv
PYTHONPATH=. uv run pytest tests/
```

### Run Specific Test Suite
```bash
# Security tests only
PYTHONPATH=. pytest tests/unit/test_security.py

# Unit tests only
PYTHONPATH=. pytest tests/unit/

# Integration tests only
PYTHONPATH=. pytest tests/integration/
```

### Run with Verbose Output
```bash
PYTHONPATH=. pytest tests/ -v
```

### Run with Coverage
```bash
PYTHONPATH=. pytest tests/ --cov=src --cov-report=html
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **test_security.py**: Security validation and protection tests
  - Path traversal prevention
  - Prompt injection detection
  - Input length limits
  - Text sanitization
  - Safe text extraction
  - State manager validation

### Integration Tests (`tests/integration/`)
_(Coming soon)_
- Full debate workflow tests
- Voting system tests
- Results generation tests
- File persistence tests

## Writing New Tests

### Unit Test Example
```python
# tests/unit/test_council_members.py

from src.council.members import get_all_members, get_member_by_id


def test_get_all_members():
    """Test that all 9 council members are loaded"""
    members = get_all_members()
    assert len(members) == 9
    assert all('name' in m for m in members)
    assert all('personality' in m for m in members)


def test_get_member_by_id():
    """Test retrieving specific council member"""
    member = get_member_by_id(1)
    assert member is not None
    assert member['name'] == 'The Pragmatist'
```

### Integration Test Example
```python
# tests/integration/test_debate_workflow.py

import pytest
from src.council.state import StateManager
from src.council.members import get_all_members


@pytest.fixture
def state_manager(tmp_path):
    """Create a temporary state manager for testing"""
    return StateManager(debates_dir=str(tmp_path))


def test_full_debate_workflow(state_manager):
    """Test complete debate from creation to results"""
    # Create debate
    debate_id = state_manager.start_new_debate("Test topic")
    assert debate_id is not None

    # Add opinions
    members = get_all_members()
    for member in members:
        state_manager.add_opinion(
            member['id'],
            member['name'],
            f"Test opinion from {member['name']}"
        )

    # Verify debate state
    current = state_manager.get_current_debate()
    assert len(current['opinions']) == 9
```

## Test Requirements

Tests should:
- Be independent and isolated
- Use fixtures for shared setup
- Have descriptive names (`test_what_when_expected`)
- Include docstrings explaining purpose
- Clean up resources (use fixtures or context managers)
- Run quickly (mock external dependencies)

## Continuous Integration

When setting up CI/CD, run tests with:

```bash
# In your CI pipeline
PYTHONPATH=. pytest tests/ -v --cov=src --cov-report=xml
```

## Adding Dependencies for Tests

If you need testing libraries:

```bash
# Add to pyproject.toml under [project.optional-dependencies]
[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",  # For async tests
]

# Install test dependencies
uv sync --extra test
```
