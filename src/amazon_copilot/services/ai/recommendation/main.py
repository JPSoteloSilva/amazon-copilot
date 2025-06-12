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

    # # Derive dominant categories for optional filtering
    # main_cats = [p.main_category for p in shopping_cart if p.main_category]
    # sub_cats = [p.sub_category for p in shopping_cart if p.sub_category]

    # main_category = Counter(main_cats).most_common(1)[0][0] if main_cats else None
    # sub_category = Counter(sub_cats).most_common(1)[0][0] if sub_cats else None

    try:
        results = qdrant_client.search_similar_products(
            query=query,
            collection_name=collection_name,
            limit=limit * 2,
            prefetch_limit=limit * 3,
        )
    except Exception:
        return []

    # Exclude existing cart items and trim to desired limit
    cart_ids = {p.id for p in shopping_cart}
    unique_results = [p for p in results if p.id not in cart_ids]

    return unique_results[:limit]
