from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import Product


def list_products(
    client: QdrantClient,
    collection_name: str = "amazon_products",
    limit: int = 10,
    offset: int = 0,
) -> list[Product]:
    """
    Retrieve a list of products from the database.

    Args:
        client: QdrantClient instance.
        collection_name: Name of the collection to retrieve products from.
        limit: Maximum number of products to retrieve.
        offset: Number of products to skip.

    Returns:
        List of Product objects.
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
    """
    Retrieve a specific product by ID from the database.

    Args:
        client: QdrantClient instance.
        collection_name: Name of the collection to retrieve the product from.
        product_id: The ID of the product to retrieve.

    Returns:
        Product object if found, None otherwise.
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
) -> tuple[list[Product], dict[int, str]]:
    """
    Add products to the database.

    Args:
        client: QdrantClient instance.
        products: List of Product objects to add.
        collection_name: Name of the collection to add the products to.
        batch_size: Number of products to add in a single batch.
        prevent_duplicates: If True, checks for existing products with the same ID and
            prevents overwriting.

    Returns:
        A tuple containing:
        - List of products that were successfully added
        - Dictionary mapping failed product IDs to failure reasons
    """
    successful_adds, failed_products = client.add_products(
        products=products,
        collection_name=collection_name,
        batch_size=batch_size,
        prevent_duplicates=prevent_duplicates,
    )
    return successful_adds, failed_products


def search_products(
    client: QdrantClient,
    query: str,
    collection_name: str = "amazon_products",
    limit: int = 10,
    offset: int = 0,
    main_category: str | None = None,
    sub_category: str | None = None,
) -> list[Product]:
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
    """
    Delete a product from the database.

    Args:
        client: QdrantClient instance.
        product_id: ID of the product to delete.
        collection_name: Name of the collection to delete the product from.

    Raises:
        Exception: If the product cannot be deleted.
    """
    client.delete_product(collection_name=collection_name, product_id=product_id)
