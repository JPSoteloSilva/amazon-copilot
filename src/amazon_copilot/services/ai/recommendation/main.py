from typing import cast

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam

from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import Product


def recommend_products(
    qdrant_client: QdrantClient,
    openai_client: OpenAI,
    collection_name: str = "amazon_products",
    shopping_cart: list[Product] | None = None,
    limit: int = 10,
) -> list[Product]:
    """Recommend products based on the user's shopping cart."""

    if shopping_cart is None or limit <= 0:
        return []

    # Build a concise summary of the cart products
    cart_summary = "; ".join(p.name for p in shopping_cart)

    # Ask the LLM for a compact keyword query
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are an usefull assistant that works with a customer's cart, "
                "Generate up to {limit} complementary Amazon products. "
                "Return ONE idea per line, plain text."
            ),
        },
        {
            "role": "user",
            "content": (f"The cart contains: {cart_summary}. "),
        },
    ]

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=0.5,
            max_tokens=200,
        )
        query = (completion.choices[0].message.content or "").strip()
        print(query)
    except OpenAIError:
        # Fall back to the cart summary if the LLM request fails
        query = cart_summary

    results = []
    for item in query.split("\n"):
        try:
            qdrant_item = qdrant_client.search_similar_products(
                query=item, collection_name=collection_name, limit=1
            )
            results.extend(qdrant_item)
        except Exception:
            return []

    if len(results) < limit:
        # If we don't have enough results, we need to get more
        try:
            more_items = qdrant_client.search_similar_products(
                query=query, collection_name=collection_name, limit=limit
            )
            results.extend(more_items)
        except Exception:
            return []

    # Exclude existing cart items and trim to desired limit
    cart_ids = {p.id for p in shopping_cart}
    unique_results = [p for p in results if p.id not in cart_ids]

    return unique_results[:limit]
