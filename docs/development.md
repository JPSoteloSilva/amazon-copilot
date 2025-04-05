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
│       ├── config.py      # Configuration management
│       ├── database.py    # Qdrant database integration
│       ├── data_loader.py # Data loading functions
│       ├── models.py      # Pydantic data models
│       └── py.typed       # Type checking marker
├── pyproject.toml         # Project configuration
└── search_products.py     # Search CLI
```

## Development Environment

### Setup with UV

We recommend using `uv` for a faster development workflow:

```bash
# Install development dependencies
uv pip install -e '.[dev]'
```

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

Format your code with Black:

```bash
black src/
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

All dependencies are managed in `pyproject.toml`:

```toml
[project]
dependencies = [
    "package-name>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "development-package>=2.0.0",
]
```

To add a new dependency:

1. Add it to `pyproject.toml`
2. Install it with `uv pip install -e .`

## Testing

We recommend writing tests for all new features using pytest:

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

## Building and Distribution

Build the package with:

```bash
hatch build
```

This will create both a wheel and a source distribution in the `dist/` directory.

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- Linting and type checking runs on every PR
- Tests run on every PR and push to main
- Code coverage is tracked

For more details, see the workflows in `.github/workflows/`.
