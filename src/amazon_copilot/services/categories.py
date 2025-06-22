from amazon_copilot.qdrant_client import QdrantClient


def list_categories(
    client: QdrantClient,
    collection_name: str = "amazon_products",
) -> dict[str, list[str]]:
    """Retrieve all main categories and their respective sub-categories from the
    collection.

    Args:
        client: The QdrantClient instance for database operations.
        collection_name: Name of the Qdrant collection to get categories from.
            Defaults to "amazon_products".

    Returns:
        Dictionary mapping main categories to their sorted list of sub-categories.
        Format: {"main_category": ["sub_category1", "sub_category2", ...]}

    Note:
        - Categories are extracted from all products in the collection
        - Sub-categories are sorted alphabetically for consistent output
        - Main categories without sub-categories will have empty lists
    """
    return client.list_categories(collection_name=collection_name)
