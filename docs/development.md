# Development Guide

This guide provides information for developers contributing to the Amazon Copilot project.

## Project Structure

```
amazon-copilot/
├── data/                  # Data directory
│   └── Amazon-Products.csv
├── docs/                  # Documentation
├── src/                   # Source code
│   └── amazon_copilot/    # Main package
│       ├── __init__.py
│       ├── api/           # API implementation
│       │   ├── main.py    # API entry point
│       │   └── routers/   # API endpoints
│       ├── services/      # Business logic services
│       ├── qdrant_client.py # Qdrant vector DB client
│       ├── cli.py         # Command-line interface
│       ├── schemas.py     # Data schemas
│       ├── utils.py       # Utility functions
│       └── py.typed       # Type checking marker
├── pyproject.toml         # Project configuration
└── docker-compose.yml     # Docker configuration
```

## Development Environment

### Setup with UV

We use `uv` for dependency management, which provides faster installation and better dependency resolution:

```bash
# Install the package in development mode
uv pip install -e .

# Sync development dependencies
uv sync --extra dev

# Sync backend dependencies
uv sync --extra backend

# Sync all dependency groups at once
uv sync --all-extras
```

When adding new dependencies, make sure to run `uv sync` to update your environment.

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install
```

## Type Safety

This project uses static type checking with mypy to ensure type safety:

### Type Checking

Run type checks with:

```bash
mypy src/amazon_copilot
```

### Type Annotations

All code should include proper type annotations:

```python
def process_data(data: list[str], limit: int = 10) -> dict[str, Any]:
    """Process the input data and return results.

    Args:
        data: List of strings to process
        limit: Maximum items to process

    Returns:
        Processed data as dictionary
    """
```

### py.typed Marker

The `py.typed` marker in the package root ensures type checkers analyze our package.

## Coding Standards

### Code Formatting

Format your code with Ruff's formatter:

```bash
ruff format src/
```

### Linting

Check code with Ruff:

```bash
ruff check src/
```

Fix Ruff issues automatically:

```bash
ruff check --fix src/
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    Extended description if needed.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When an invalid value is provided
    """
```

## Dependency Management

Dependencies are defined in the `pyproject.toml` file, organized into groups:

```toml
[project]
dependencies = [
    # Core dependencies
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    # Development dependencies
    "mypy>=1.7.0",
    "ruff>=0.1.5",
]
backend = [
    # Backend dependencies
    "qdrant-client>=1.6.0",
    "fastembed>=0.6.1",
    "fastapi>=0.115.12",
]
```

To add a new dependency:

```bash
uv add --extra <group_name> <dependency>
```

## Testing

Write tests for all new features using pytest:

```python
# test_module.py
def test_my_function():
    """Test that my_function works correctly."""
    result = my_function("test", 42)
    assert result is True
```

Run tests with:

```bash
pytest
```

## API Development

When developing API endpoints:

1. Create route definitions in `src/amazon_copilot/api/routers/`
2. Include the router in `main.py`
3. Implement business logic in the `services` module

Example:

```python
# src/amazon_copilot/api/routers/products.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
async def list_products():
    """List all products."""
    # Implementation
```

## Building and Distribution

Build the package with:

```bash
uv pip build
```

This will create both a wheel and a source distribution in the `dist/` directory.

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- Linting and type checking runs on every PR
- Tests run on every PR and push to main
- Code coverage is tracked

For more details, see the workflows in `.github/workflows/`.
