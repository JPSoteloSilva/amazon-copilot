# Search Guide

This guide explains how to search for products using the Amazon Copilot system.

## Search CLI

Amazon Copilot provides a command-line interface for searching products using semantic similarity.

### Basic Search

To search for products:

```bash
./search_products.py "your search query"
```

For example:

```bash
./search_products.py "wireless headphones with noise cancellation"
```

### Search Parameters

You can specify the maximum number of results to return:

```bash
./search_products.py "smartphone" --limit 10
```

## How Search Works

Amazon Copilot uses semantic search rather than keyword matching:

1. Your search query is converted to a vector embedding using the sentence-transformers model
2. This embedding is compared to product embeddings stored in Qdrant
3. Products are ranked by similarity (cosine similarity) to your query
4. The most similar products are returned

## Example Output

```
Searching for products similar to: 'wireless headphones'
Returning up to 5 results
--------------------------------------------------

1. Sony WH-1000XM4 Wireless Noise Cancelling Headphones
   Category: electronics > Headphones
   Price: ₹29,990 (Original: ₹33,990)
   Rating: 4.7 (3,152 ratings)
   Similarity: 0.8523
   Link: https://www.amazon.in/Sony-WH-1000XM4-Cancelling-Headphones-Blue

2. boAt Rockerz 450 Bluetooth On-Ear Headphones with Mic
   Category: electronics > Headphones
   Price: ₹1,499 (Original: ₹3,990)
   Rating: 4.2 (42,569 ratings)
   Similarity: 0.7890
   Link: https://www.amazon.in/boAt-Rockerz-450-Headphone-Cancellation
```

## Search Tips

### Effective Queries

- **Use natural language**: "comfortable headphones for running" works better than "headphones running"
- **Include important features**: "smartphone with good camera" is better than just "smartphone"
- **Specify price ranges**: "budget-friendly laptop" or "premium smartphone"

### Interpreting Results

- **Similarity score**: Higher values (closer to 1.0) indicate better matches
- **Unexpected results**: The semantic search might return products that don't contain your exact keywords but are contextually related

## Advanced Usage

### Programmatic Search

You can use the search functionality in your Python code:

```python
from amazon_copilot.database import QdrantService

# Initialize Qdrant service
qdrant = QdrantService()

# Search for products
results = qdrant.search_similar_products("gaming laptop", limit=5)

# Process results
for result in results:
    print(f"Product: {result.product.name}")
    print(f"Price: {result.product.discount_price}")
    print(f"Link: {result.product.link}")
    print("---")
```

## Troubleshooting

### No Results Returned

If your search returns no results:

- Ensure you've loaded data into the database (see [Data Loading Guide](data_loading.md))
- Try more general search terms
- Check that Qdrant is running correctly

### Low Relevance Results

If the results don't seem relevant:

- Try to be more specific in your query
- Check the similarity scores - low scores (below 0.5) may indicate poor matches
