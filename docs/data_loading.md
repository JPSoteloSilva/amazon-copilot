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
python -m amazon_copilot.data_loader
```

This will:
1. Read the entire CSV file
2. Convert records to AmazonProduct objects
3. Generate embeddings for each product
4. Store products and embeddings in Qdrant

### Loading a Subset of Data

For testing or development, you may want to load only a subset of the data:

```bash
python -m amazon_copilot.data_loader --nrows 100
```

This loads only the first 100 rows from the CSV file.

### Loading Process

During loading, you'll see progress information:

```
Loading data from data/Amazon-Products.csv
Loaded 100 rows from CSV
Created 98 valid product objects
Added 10/98 products to the database
Added 20/98 products to the database
...
Successfully added 98 products to the database
```

## Customizing Data Sources

### Using a Different CSV File

You can modify the path to the CSV file in the `data_loader.py` script:

```python
# In data_loader.py
csv_path = os.path.join(root_dir, "path/to/your/file.csv")
```

### Data Processing Pipeline

The data loading process consists of these steps:

1. **Loading CSV data** (`load_csv` function)
2. **Processing data into models** (`process_dataframe` function)
3. **Generating embeddings** (handled by `QdrantService.generate_embedding`)
4. **Storing in database** (handled by `QdrantService.add_product`)

## Troubleshooting

### CSV Import Issues

If you encounter issues with the CSV import:

- Check that the CSV file exists in the expected location
- Verify that the CSV format matches the expected columns
- Try using the `--nrows` parameter to load a small subset for testing

### Embedding Issues

If embedding generation fails:

- Ensure internet connectivity (needed to download the embedding model)
- Check available disk space (the model requires approximately 100MB)

### Database Issues

If you have trouble adding products to the database:

- Verify that Qdrant is running (`curl http://localhost:6333/healthz`)
- Check the Qdrant logs: `docker logs amazon-qdrant`
- Restart Qdrant: `docker restart amazon-qdrant`
