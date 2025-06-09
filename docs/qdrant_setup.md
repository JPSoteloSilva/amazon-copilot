# Qdrant Setup Guide

This guide explains how to set up and configure Qdrant for use with Amazon Copilot.

## Overview

[Qdrant](https://qdrant.tech/) is a vector similarity search engine used in this project to store product embeddings and perform semantic searches.

## Running Qdrant

### Option 1: Docker Container

The simplest way to run Qdrant is using Docker:

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name amazon-qdrant qdrant/qdrant
```

This command:
- `-d`: Runs the container in detached mode (background)
- `-p 6333:6333`: Maps HTTP API port
- `-p 6334:6334`: Maps gRPC port
- `-v $(pwd)/qdrant_storage:/qdrant/storage`: Mounts a volume for data persistence
- `--name amazon-qdrant`: Names the container

### Option 2: Docker Compose (Recommended)

The project includes a `docker-compose.yml` file for easier management:

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

## Verifying Qdrant is Running

Check the Qdrant status with:

```bash
# HTTP health check
curl http://localhost:6333/healthz

# Check container status
docker ps | grep qdrant
```

The response should be: `{"ok":true}`

## Collection Management

Collections in Qdrant are used to store vector embeddings and provide search functionality.

### Collection Configuration

When created with the CLI, collections are configured with:
- Vector dimension: 384 (for the default model)
- Distance metric: Cosine similarity
- On-disk storage for vectors
- Scalar filtering fields for categories

### Creating Collections

Collections are created automatically when needed, but you can manually create them:

```bash
amazon-copilot create-collection amazon_products
```

This command establishes the proper schema for semantic product search.

## Qdrant Configuration

The Qdrant client is configured using environment variables or the `.env` file:

```
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=amazon_products
```

## Qdrant Dashboard

Qdrant includes a web dashboard for visualization and management:

1. Access the dashboard at `http://localhost:6333/dashboard`
2. Use it to:
   - View collections and their configurations
   - Explore vectors and points
   - Perform test searches
   - Monitor cluster health

## Monitoring and Maintenance

### Checking Collection Info

```bash
curl http://localhost:6333/collections/amazon_products
```

### Viewing Logs

```bash
docker logs amazon-qdrant
```

### Container Management

```bash
# Stop the container
docker stop amazon-qdrant

# Start the container
docker start amazon-qdrant

# Restart the container
docker restart amazon-qdrant

# Remove the container (deletes data if volume not used)
docker rm -f amazon-qdrant
```

## Troubleshooting

### Connection Issues

If you can't connect to Qdrant:
- Check if Docker is running
- Verify the container is up with `docker ps`
- Ensure ports 6333 and 6334 are not in use by other services

### Data Persistence

If your data disappears after restarting:
- Make sure you're using volume mounting with `-v $(pwd)/qdrant_storage:/qdrant/storage`
- Check the permissions on your host directory

### Performance Issues

If search is slow:
- Consider adjusting the vector dimensions or index type
- Try reducing the number of points in your collection
- Add more filters to narrow search scope
