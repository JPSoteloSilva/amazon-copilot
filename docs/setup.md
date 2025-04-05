# Detailed Setup Guide

This guide provides comprehensive setup instructions for the Amazon Copilot project.

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
   uv pip install -e .
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

## Database Setup

### Option 1: Run Standalone Qdrant Container

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name amazon-qdrant qdrant/qdrant
```

### Option 2: Use Docker Compose (Recommended)

The project includes a `docker-compose.yml` file that sets up both the Qdrant database and the application in containers:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

This approach offers several advantages:
- Automatically configures the network between services
- Sets environment variables correctly
- Provides health checks for dependencies
- Mounts volumes for persistent data

### Verify Qdrant is running

```bash
# Check if container is running
docker ps | grep qdrant

# Check Qdrant API
curl http://localhost:6333/healthz
```

The response should be: `{"ok":true}`

## Development Tools

### Type Checking

```bash
# Run mypy type checker
mypy src/amazon_copilot
```

### Code Formatting

```bash
# Install development dependencies
uv pip install '.[dev]'

# Format code with black
black src/

# Run linter
ruff check src/
```

## Containerization

The project includes a Dockerfile that allows you to build and run the application in a container:

```bash
# Build the image
docker build -t amazon-copilot .

# Run container
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -e QDRANT_HOST=host.docker.internal \
  amazon-copilot
```

For more advanced usage, the `docker-compose.yml` file provides a complete setup for both the application and the Qdrant database.

## Troubleshooting

### Common Issues

1. **Qdrant connection refused**:
   - Ensure Docker is running
   - Check if Qdrant container is active: `docker ps`
   - Restart the container: `docker restart amazon-qdrant`

2. **Missing dependencies**:
   - Reinstall with development extras: `uv pip install -e '.[dev]'`

3. **Python version mismatch**:
   - Verify Python version: `python --version`
   - Ensure pyenv is properly configured: `pyenv version`

4. **Docker networking issues**:
   - When running the app outside Docker but Qdrant inside Docker, use `localhost` as the host
   - When running both services with Docker Compose, the service name `qdrant` should be used as the host
   - When running the app in Docker but Qdrant outside, use `host.docker.internal` as the host
