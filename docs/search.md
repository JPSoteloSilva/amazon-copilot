# Search Guide

This guide explains how to use the search functionality in Amazon Copilot.

## Basic Search

The simplest way to search for products is using the CLI:

```bash
amazon-copilot search-products "wireless headphones" --collection-name amazon_products
```

This performs a semantic search using embeddings stored in the Qdrant vector database.

## Search Parameters

The search command supports several parameters:

```bash
amazon-copilot search-products "wireless headphones" amazon_products \
  --main-category "Electronics" \
  --sub-category "Headphones" \
  --limit 20 \
  --offset 0
```

### Available Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query text (required) | - |
| `collection_name` | Name of the collection to search (required) | - |
| `main_category` | Filter by main category | No filter |
| `sub_category` | Filter by sub-category | No filter |
| `limit` | Maximum number of results to return | 10 |
| `offset` | Number of results to skip for pagination | 0 |

## Search Techniques

### Semantic Search

The search uses vector similarity rather than just keyword matching:

1. Your search query is converted into a vector embedding
2. The database finds products with embeddings similar to your query
3. Results are ordered by similarity score

This allows for more intelligent searches that understand the meaning behind your query. For example:
- "portable audio device" might return results for "MP3 player"
- "device for listening to music while jogging" might return results for "wireless earbuds"

### Filtering

To narrow down search results, combine semantic search with category filtering:

```bash
amazon-copilot search-products "wireless" --main-category "Electronics" --sub-category "Headphones"
```

This first finds semantically similar products, then applies the category filters.

### Pagination

For large result sets, use pagination with the `limit` and `offset` parameters:

```bash
# First page (results 1-10)
amazon-copilot search-products "wireless" --limit 10 --offset 0

# Second page (results 11-20)
amazon-copilot search-products "wireless" --limit 10 --offset 10
```

## Search Results

Search results are displayed in a table format with product details:

```
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ ID   ┃ Name                                      ┃ Category                                 ┃ Price ($) ┃ Rating ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│ 1024 │ Bose QuietComfort 45 Bluetooth Wireless   │ Electronics > Headphones                │ 329.00    │ 4.7    │
│      │ Noise Cancelling Headphones               │                                         │           │ (9854) │
│ 2945 │ Sony WH-1000XM4 Wireless Premium Noise    │ Electronics > Headphones                │ 348.00    │ 4.8    │
│      │ Canceling Overhead Headphones             │                                         │           │ (12587)│
│ 5832 │ Beats Studio3 Wireless Noise Cancelling   │ Electronics > Headphones                │ 199.95    │ 4.5    │
│      │ Over-Ear Headphones                       │                                         │           │ (7426) │
└──────┴────────────────────────────────────────────┴─────────────────────────────────────────┴───────────┴────────┘
```

## API Search

The project includes a REST API for search, which can be used in web applications.

### API Endpoints

#### Search Products

```
GET /products/search
```

Query parameters:
- `query`: Search text
- `main_category`: (Optional) Filter by main category
- `sub_category`: (Optional) Filter by sub category
- `limit`: (Optional) Maximum results to return
- `offset`: (Optional) Results to skip for pagination

Example request:

```bash
curl -X GET "http://localhost:8000/products/search?query=wireless+headphones&limit=5" -H "accept: application/json"
```

#### API Response Format

```json
{
  "results": [
    {
      "id": 1024,
      "name": "Bose QuietComfort 45 Bluetooth Wireless Noise Cancelling Headphones",
      "main_category": "Electronics",
      "sub_category": "Headphones",
      "image": "https://example.com/image1.jpg",
      "link": "https://example.com/product1",
      "ratings": 4.7,
      "no_of_ratings": 9854,
      "discount_price": 329.0,
      "actual_price": 379.0
    },
    {
      "id": 2945,
      "name": "Sony WH-1000XM4 Wireless Premium Noise Canceling Overhead Headphones",
      "main_category": "Electronics",
      "sub_category": "Headphones",
      "image": "https://example.com/image2.jpg",
      "link": "https://example.com/product2",
      "ratings": 4.8,
      "no_of_ratings": 12587,
      "discount_price": 348.0,
      "actual_price": 399.99
    }
  ],
  "total": 2,
  "limit": 5,
  "offset": 0
}
```

## Advanced Usage

### Query Optimization

For better search results:

1. **Be specific**: Include details like brand, color, or features
2. **Use natural language**: The semantic search works well with conversational queries
3. **Combine with filters**: Use category filters to narrow results

### Performance Tips

For optimal search performance:

1. Use category filters to reduce the search space
2. Keep collection sizes reasonable (under 1 million products per collection)
3. Adjust pagination settings based on UI requirements

## Troubleshooting

### Common Search Issues

1. **No results found**:
   - Ensure data is loaded in the collection
   - Try broader search terms
   - Check that category filters aren't too restrictive

2. **Irrelevant results**:
   - Make your query more specific
   - Add category filters
   - Check embedding model configuration

3. **Slow performance**:
   - Reduce the size of your collection
   - Use more specific search terms
   - Add filtering to reduce the search space
