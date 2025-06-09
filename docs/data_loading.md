# Data Loading Guide

This guide explains how to load product data into the Amazon Copilot system.

## Data Format

Amazon Copilot expects CSV data with the following columns:

- `id`: Unique product identifier
- `name`: Product name
- `main_category`: Main product category
- `sub_category`: Product sub-category
- `image`: URL to product image
- `link`: URL to product page
- `ratings`: Product rating (0-5)
- `no_of_ratings`: Number of ratings
- `discount_price`: Discounted price
- `actual_price`: Original price

## Sample Data

The project includes a sample dataset in `data/Amazon-Products.csv`. This file contains product data scraped from Amazon.

## Loading Data

### Basic Data Loading

To load data into the Qdrant vector database:

```bash
amazon-copilot load-products data/Amazon-Products.csv amazon_products
```

This will:
1. Read the entire CSV file
2. Convert records to product objects
3. Generate embeddings for each product
4. Store products and embeddings in Qdrant

### Loading Options

The load-products command supports several options:

| Option | Description | Default |
|--------|-------------|---------|
| `--nrows` | Limit the number of rows to load | All rows |
| `--skiprows` | Skip the first N rows | 0 |
| `--batch-size` | Number of products to process at once | 100 |
| `--model-name` | Embedding model to use | Value from .env |

### Loading a Subset of Data

For testing or development, load only a subset of the data:

```bash
amazon-copilot load-products data/Amazon-Products.csv amazon_products --nrows 100
```

### Loading with Batch Processing

For larger datasets, specify a batch size to control memory usage:

```bash
amazon-copilot load-products data/Amazon-Products.csv amazon_products --batch-size 500
```

### Resuming Failed Loads

If a loading process fails, you can skip already processed rows:

```bash
amazon-copilot load-products data/Amazon-Products.csv amazon_products --skiprows 1000
```

### Loading Process Monitoring

During loading, you'll see progress information:

```
Loading products from 'data/Amazon-Products.csv' into collection 'amazon_products'
Loaded 100 rows from CSV
Created 98 valid product objects
Added 10/98 products to the database
Added 20/98 products to the database
...
Products loaded successfully: 98
```

## Data Processing Details

### Embedding Generation

When loading data, the system:

1. Uses the fastembed library to generate text embeddings
2. By default, uses the all-MiniLM-L6-v2 model (384-dimensional vectors)
3. Performs normalization on the embeddings
4. Processes items in batches to optimize memory usage

### Data Validation

During import, records are validated to ensure:
- Required fields are present
- Numeric fields can be converted to proper types
- IDs are unique

Invalid records are skipped with warnings.

## Collection Management

### Creating Collections

Before loading data, ensure your collection exists:

```bash
amazon-copilot create-collection amazon_products
```

The system will automatically create collections when needed, but pre-creating them allows you to verify configuration.

### Deleting Collections

To remove all data and delete a collection:

```bash
amazon-copilot delete-collection amazon_products --force
```

Use the `--force` flag to bypass the confirmation prompt.

## Troubleshooting

### CSV Import Issues

If you encounter issues with the CSV import:

- Check that the CSV file exists in the expected location
- Verify that the CSV format matches the expected columns
- Try using the `--nrows` parameter to load a small subset for testing

### Embedding Issues

If embedding generation fails:

- Ensure internet connectivity (needed to download the embedding model)
- Check available disk space (the embedding model requires approximately 100MB)
- Verify that you've installed the backend dependencies with `uv sync --extra backend`

### Memory Management

For very large datasets:
- Use smaller batch sizes (e.g., `--batch-size 50`)
- Process the data in chunks using `--nrows` and `--skiprows`
- Consider using a machine with more RAM
