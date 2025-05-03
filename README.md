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

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Start Qdrant database**:
   ```bash
   # Option 1: Run standalone Qdrant container
   docker run -d -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage \
     --name amazon-qdrant qdrant/qdrant

   # Option 2: Use Docker Compose (sets up both Qdrant and the app)
   docker-compose up -d
   ```

4. **Create environment variables**:
   ```bash
   cp .env.example .env
   ```

## Basic Usage

### 1. Load product data

```bash
python -m amazon_copilot.data_loader --nrows 100
```

### 2. Search for products

```bash
./search_products.py "wireless headphones"
```

## API Usage

Run the FastAPI development server:

```bash
uv run fastapi dev src/amazon_copilot/api/main.py
```

This will start the API server in development mode with automatic reloading. You can access the API documentation at http://localhost:8000/docs after starting the server.

## Documentation

- [Detailed Setup Guide](docs/setup.md)
- [Data Loading Guide](docs/data_loading.md)
- [Search Guide](docs/search.md)
- [Development Guide](docs/development.md)

## Project Structure

```
amazon-copilot/
├── src/amazon_copilot/    
│   ├── api/               
│   │   ├── main.py       
│   │   ├── routers/       
│   |   |   └── products.py                   
│   │   ├── crud/       
│   |   |   └── products.py                   
│   ├── qdrant/           
│   │   ├── client.py      
│   │   └── utils.py
│   └── shared/              
|       └── schemas.py                  
├── data/                  
├── docs/                  
├── pyproject.toml         
├── docker-compose.yml     
├── Dockerfile             
└── search_products.py     
```

## License

[MIT License](LICENSE)
