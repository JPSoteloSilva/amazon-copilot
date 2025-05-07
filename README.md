# Amazon Copilot

A vector-based search system for Amazon product data using Qdrant for similarity search and sentence-transformers for embedding generation.

## Features

- Semantic search for Amazon products
- Vector embeddings with sentence-transformers
- Fast similarity search with Qdrant
- Type-safe Python codebase
- Command-line interface

## Quick Setup

### Prerequisites

- Python 3.12+
- Docker

### Installation

1. **Setup Python environment with pyenv**:
   ```bash
   # Install Python 3.12
   pyenv install 3.12.2

   # Set local Python version
   pyenv local 3.12.2
   ```

2. **Install dependencies with uv**:
   ```bash
   # Install uv if you don't have it
   pip install uv

   # Create virtual environment
   uv venv

   # Activate virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Sync dependencies with specific extras
   uv sync --extra dev --extra backend

   # Or sync all dependency groups at once
   uv sync --all-extras
   ```

3. **Start Qdrant database**:
   ```bash
   # Use Docker Compose (recommended)
   docker-compose up -d
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

## Basic Usage

### 1. Create collection and load data

```bash
# Create a collection
amazon-copilot create-collection amazon_products

# Load product data from CSV
amazon-copilot load-products data/Amazon-Products.csv amazon_products
```

### 2. Search for products

```bash
# Search using the CLI
amazon-copilot search-products "wireless headphones" --collection-name amazon_products
```

### 3. API Usage

Run the FastAPI development server:

```bash
uvicorn amazon_copilot.api.main:app --reload
```

Access the API documentation at http://localhost:8000/docs

## Documentation

For detailed guides, refer to:

- [Detailed Setup Guide](docs/setup.md) - Full installation instructions
- [Data Loading Guide](docs/data_loading.md) - How to load and manage product data
- [Search Guide](docs/search.md) - Advanced search options and filtering
- [Development Guide](docs/development.md) - For contributors and developers
- [Qdrant Setup Guide](docs/qdrant_setup.md) - Vector database configuration

## Project Structure

```
amazon-copilot/
├── src/amazon_copilot/
│   ├── api/               # FastAPI implementation
│   │   ├── main.py        # API entry point
│   │   └── routers/       # API route definitions
│   ├── services/          # Business logic services
│   ├── qdrant_client.py   # Qdrant vector DB client
│   ├── cli.py             # Command-line interface
│   ├── schemas.py         # Data schemas
│   └── utils.py           # Utility functions
├── data/                  # Data directory
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
├── docker-compose.yml     # Docker configuration
└── README.md              # This file
```

## License

[MIT License](LICENSE)
