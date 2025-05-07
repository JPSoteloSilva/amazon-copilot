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

    # The get_product method is async, so we need to await it
    return client.get_product(collection_name=collection_name, product_id=product_id)


def add_products(
    client: QdrantClient,
    products: list[Product],
    collection_name: str = "amazon_products",
    batch_size: int = 100,
) -> int:
    """
    Add products to the database.

    Args:
        client: QdrantClient instance.
        products: List of Product objects to add.
        collection_name: Name of the collection to add the products to.
        batch_size: Number of products to add in a single batch.

    Returns:
        Number of products added successfully.
    """
    successful_adds = client.add_products(
        products=products,
        collection_name=collection_name,
        batch_size=batch_size,
    )
    return successful_adds


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
) -> bool:
    return client.delete_product(collection_name=collection_name, product_id=product_id)
