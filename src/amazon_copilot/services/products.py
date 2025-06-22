from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import AddProductsResponse, Product


def list_products(
    client: QdrantClient,
    collection_name: str = "amazon_products",
    limit: int = 10,
    offset: int = 0,
    query: str | None = None,
    main_category: str | None = None,
    sub_category: str | None = None,
) -> list[Product]:
    """Unified function to retrieve products with optional search and filtering.

    This function can either list all products (when query is None) or search for
    products based on a query (when query is provided). Category filtering can be
    applied in both modes.

    Args:
        client: The QdrantClient instance for database operations.
        collection_name: Name of the Qdrant collection containing products.
            Defaults to "amazon_products".
        limit: Maximum number of products to retrieve. If None, returns all results.
            Defaults to 10.
        offset: Number of products to skip for pagination. Defaults to 0.
        query: Optional search query text. If None, returns all products.
            If provided, performs semantic search.
        main_category: Optional filter by main product category (e.g., "Electronics").
        sub_category: Optional filter by sub product category (e.g., "Smartphones").

    Returns:
        A list of Product objects. If query is provided, results are ordered by
        relevance. If no query, results are in database order.

    Note:
        - When query is None: Returns products in database order with optional category
        filtering.
        - When query is provided: Performs hybrid search with relevance ranking and
        optional category filtering.
        - Category filters work in both modes.
        - main_category must be defined if sub_category is defined.
    """
    return client.list_products(
        collection_name=collection_name,
        query=query,
        limit=limit,
        offset=offset,
        main_category=main_category,
        sub_category=sub_category,
    )


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
