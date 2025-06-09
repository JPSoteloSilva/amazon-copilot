# Detailed Setup Guide

This guide provides comprehensive setup instructions for the Amazon Copilot project, expanding on the quick setup in the README.

## Prerequisites

### Python Setup with pyenv

[pyenv](https://github.com/pyenv/pyenv) lets you easily switch between multiple versions of Python:

#### Install pyenv

**macOS**:
```bash
brew install pyenv
```

**Linux**:
```bash
curl https://pyenv.run | bash
```

**Windows**:
```bash
pip install pyenv-win
```

#### Configure pyenv

Add to your shell configuration file (`.bashrc`, `.zshrc`, etc.):

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

#### Install Python with pyenv

```bash
# List available Python versions
pyenv install --list

# Install Python 3.12.2
pyenv install 3.12.2

# Set local Python version for this project
cd /path/to/amazon-copilot
pyenv local 3.12.2
```

### Docker Setup

Docker is required to run the Qdrant vector database:

**macOS/Windows**:
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Linux**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## Installation

### UV Package Manager

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver:

```bash
# Install uv
pip install uv

# Verify installation
uv --version
```

### Project Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/amazon-copilot.git
   cd amazon-copilot
   ```

2. **Create and activate a virtual environment with uv**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install project dependencies with uv**:
   ```bash
   # Sync all dependency groups
   uv sync --all-extras

   # Or install specific dependency groups
   uv sync --extra dev     # Development tools
   uv sync --extra backend # Backend dependencies
   ```

4. **Environment configuration**:
   ```bash
   cp .env.example .env
   ```

   You can edit `.env` to customize settings:
   ```
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   COLLECTION_NAME=amazon_products
   MODEL_NAME=all-MiniLM-L6-v2
   ```

## Running the API

To run the FastAPI development server:

```bash
uvicorn amazon_copilot.api.main:app --reload
```

Access the API documentation at http://localhost:8000/docs

## Development Tools

### Type Checking

```bash
# Run mypy type checker
mypy src/amazon_copilot
```

### Code Formatting and Linting

```bash
# Format code with ruff
ruff format src/

# Run linter
ruff check src/
```

## Troubleshooting

### Common Issues

1. **Python version mismatch**:
   - Verify Python version: `python --version`
   - Ensure pyenv is properly configured: `pyenv version`

2. **Missing dependencies**:
   - Ensure you've installed all dependencies: `uv sync --all-extras`
   - Check for errors in the installation logs

3. **Docker networking issues**:
   - When running the app outside Docker but Qdrant inside Docker, use `localhost` as the host
   - When running both services with Docker Compose, the service name `qdrant` should be used as the host

4. **Permission Issues**:
   - On Linux/macOS, you might need to run some commands with `sudo`
   - For Docker volume mounting issues, check file ownership and permissions

5. **Installation Failures**:
   - If `uv` installation fails, you can use pip as a fallback: `pip install -e .[dev,backend]`
   - For SSL errors, ensure your certificates are up to date
