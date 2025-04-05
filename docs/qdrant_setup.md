# Qdrant Vector Database Setup

This document explains how to set up and use the Qdrant vector database for the Amazon Copilot project.

## Overview

The project uses Qdrant to store product information along with vector embeddings of product names. These embeddings enable semantic search capabilities, allowing users to find products similar to their queries.

## Components

1. **Docker Compose**: Sets up Qdrant in a containerized environment
2. **QdrantService**: A Python service class that interacts with Qdrant
3. **Data Loader**: A script to load Amazon product data from CSV into Qdrant

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.12+

### Running the Setup

1. Make sure Docker is running on your system
2. Start the containers:

```bash
docker-compose up -d
```

3. The data loader will automatically run within the application container

### Accessing Qdrant

- Qdrant API is available at: http://localhost:6333
- Qdrant web UI is available at: http://localhost:6333/dashboard

## Implementation Details

### Embedding Model

We use the `all-MiniLM-L6-v2` model from SentenceTransformers to create embeddings for product names. This model:

- Generates 384-dimensional embeddings
- Is optimized for semantic similarity tasks
- Provides a good balance between quality and performance

### Collection Structure

The Amazon products are stored in a collection named `amazon_products` with:

- 384-dimensional vectors using cosine similarity
- Product metadata stored in the payload
- Product ID used as the point ID

## Usage Examples

### Searching for Similar Products

```python
from amazon_copilot.database import QdrantService

# Initialize service
qdrant = QdrantService()

# Search for products
results = qdrant.search_similar_products("wireless headphones", limit=5)

# Display results
for i, result in enumerate(results):
    print(f"{i+1}. {result.product.name}")
```

## Troubleshooting

- If the Qdrant container fails to start, check Docker logs: `docker logs qdrant`
- If connection issues occur, verify that the QDRANT_HOST and QDRANT_PORT in .env match the Docker Compose configuration
