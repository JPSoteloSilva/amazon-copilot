import json


def list_categories(collection_name: str) -> dict[str, list[str]]:
    """Retrieve all main categories and their respective sub-categories from the
    categories.json file.

    Returns:
        Dictionary mapping main categories to their sorted list of sub-categories.
        Format: {"main_category": ["sub_category1", "sub_category2", ...]}

    Note:
        - Categories are extracted from all products in the collection
        - Sub-categories are sorted alphabetically for consistent output
        - Main categories without sub-categories will have empty lists
    """
    if collection_name == "amazon_products":
        with open("src/amazon_copilot/services/data/categories.json") as f:
            return json.load(f)
    else:
        raise ValueError(f"Collection name {collection_name} not found")
