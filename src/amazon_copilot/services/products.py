from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import AddProductsResponse, Product


def list_products(
    client: QdrantClient,
    collection_name: str = "amazon_products",
    limit: int = 10,
    offset: int = 0,
) -> list[Product]:
    """Retrieve a paginated list of products from the vector database.

    This function provides pagination support for browsing through the product
    collection without requiring a search query.

    Args:
        client: The QdrantClient instance for database operations.
        collection_name: Name of the Qdrant collection containing products.
            Defaults to "amazon_products".
        limit: Maximum number of products to retrieve (1-100). Defaults to 10.
        offset: Number of products to skip for pagination. Defaults to 0.

    Returns:
        A list of Product objects containing product information including
        ID, name, categories, pricing, and ratings.

    Note:
        Results are returned in the order they exist in the database.
        Use search_products() for relevance-based ordering.
    """
    # Use empty query to get all products
    responses = client.list_products(
        collection_name=collection_name,
        limit=limit,
        offset=offset,
    )

    return responses


def get_product(
    client: QdrantClient,
    collection_name: str = "amazon_products",
    product_id: int = 0,
) -> Product:
    """Retrieve a specific product by its unique ID.

    Args:
        client: The QdrantClient instance for database operations.
        collection_name: Name of the Qdrant collection containing products.
            Defaults to "amazon_products".
        product_id: The unique identifier of the product to retrieve.

    Returns:
        Product object containing all product information.

    Raises:
        ValueError: If the product with the specified ID is not found in the collection.
    """
    try:
        return client.get_product(
            collection_name=collection_name, product_id=product_id
        )
    except ValueError as e:
        raise ValueError(f"Product with id {product_id} not found") from e


def add_products(
    client: QdrantClient,
    products: list[Product],
    collection_name: str = "amazon_products",
    batch_size: int = 100,
    prevent_duplicates: bool = True,
) -> AddProductsResponse:
    """Add multiple products to the vector database with comprehensive error tracking.

    This function processes products in batches, generates embeddings, and stores
    them in the vector database. It provides detailed feedback on which products
    were successfully added and which failed with specific error reasons.

    Args:
        client: The QdrantClient instance for database operations.
        products: List of Product objects to add to the collection.
        collection_name: Name of the Qdrant collection to store products.
            Defaults to "amazon_products".
        batch_size: Number of products to process in each batch. Larger batches
            improve performance but use more memory. Defaults to 100.
        prevent_duplicates: Whether to check for existing product IDs and prevent
            overwriting. When True, existing products are marked as failed.
            Defaults to True.

    Returns:
        AddProductsResponse containing:
            - successful: List of Product objects that were successfully added
            - failed: Dict mapping product IDs to error messages for failed additions

    Note:
        - Products are processed using dense and sparse embeddings for hybrid search
        - Batch processing continues even if individual batches fail
        - All errors are captured and reported in the response
    """
    successful_adds, failed_products = client.add_products(
        products=products,
        collection_name=collection_name,
        batch_size=batch_size,
        prevent_duplicates=prevent_duplicates,
    )
    return AddProductsResponse(successful=successful_adds, failed=failed_products)


def search_products(
    client: QdrantClient,
    query: str,
    collection_name: str = "amazon_products",
    limit: int = 10,
    offset: int = 0,
    main_category: str | None = None,
    sub_category: str | None = None,
) -> list[Product]:
    """Search for products using hybrid vector search with optional category filtering.

    This function performs semantic search using both dense and sparse embeddings
    to find products most relevant to the query text. Results are ranked by
    relevance using Reciprocal Rank Fusion (RRF).

    Args:
        client: The QdrantClient instance for database operations.
        query: Search query text to find relevant products.
        collection_name: Name of the Qdrant collection to search.
            Defaults to "amazon_products".
        limit: Maximum number of results to return. Defaults to 10.
        offset: Number of results to skip for pagination. Defaults to 0.
        main_category: Optional filter by main product category (e.g., "Electronics").
        sub_category: Optional filter by sub product category (e.g., "Smartphones").

    Returns:
        List of Product objects ordered by relevance to the search query.
        Empty list if no matching products are found.

    Note:
        - Uses hybrid search combining dense (semantic) and sparse (keyword) matching
        - Category filters are applied as exact text matches
        - Results are automatically reranked for optimal relevance
    """
    return client.search_similar_products(
        query=query,
        collection_name=collection_name,
        limit=limit,
        offset=offset,
        main_category=main_category,
        sub_category=sub_category,
    )


def delete_product(
    client: QdrantClient,
    product_id: int,
    collection_name: str = "amazon_products",
) -> None:
    """Delete a specific product from the vector database.

    Args:
        client: The QdrantClient instance for database operations.
        product_id: The unique identifier of the product to delete.
        collection_name: Name of the Qdrant collection containing the product.
            Defaults to "amazon_products".

    Raises:
        ValueError: If the product with the specified ID is not found.
        Exception: If the deletion operation fails due to database errors.

    Note:
        This operation permanently removes the product and its embeddings.
        The deletion cannot be undone.
    """
    client.delete_product(collection_name=collection_name, product_id=product_id)
