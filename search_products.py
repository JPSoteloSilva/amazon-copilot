#!/usr/bin/env python
"""Script to search for products using vector similarity."""

import argparse
import sys

from amazon_copilot.database import QdrantService


def search(query: str, limit: int = 5) -> None:
    """Search for products similar to the query.

    Args:
        query: The search query
        limit: Maximum number of results to return
    """
    print(f"Searching for products similar to: '{query}'")
    print(f"Returning up to {limit} results")
    print("-" * 50)

    # Initialize Qdrant service
    qdrant_service = QdrantService()

    # Search for similar products
    results = qdrant_service.search_similar_products(query, limit=limit)

    # Display results
    if not results:
        print("No results found")
        return

    for i, result in enumerate(results):
        product = result.product
        # Calculate dot product of first 10 dimensions as simple similarity measure
        similarity = sum(
            x * y
            for x, y in zip(result.embedding[:10], result.embedding[:10], strict=False)
        )
        similarity_normalized = similarity / 10  # Normalize for display

        print(f"\n{i + 1}. {product.name}")
        print(f"   Category: {product.main_category} > {product.sub_category}")
        print(f"   Price: {product.discount_price} (Original: {product.actual_price})")
        print(f"   Rating: {product.ratings} ({product.no_of_ratings} ratings)")
        print(f"   Similarity: {similarity_normalized:.4f}")
        print(f"   Link: {product.link}")


def main() -> None:
    """Run the search script."""
    parser = argparse.ArgumentParser(
        description="Search for products using vector similarity"
    )
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument(
        "--limit", type=int, default=5, help="Maximum number of results to return"
    )

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    search(args.query, args.limit)


if __name__ == "__main__":
    main()
