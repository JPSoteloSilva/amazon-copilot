from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query, status
from openai import OpenAI

from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import Product
from amazon_copilot.services.ai.recommendation.main import recommend_products
from amazon_copilot.utils import get_qdrant_client

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

load_dotenv()

# Dependency to reuse singleton clients
qdrant_client_dependency = Depends(get_qdrant_client)
openai_client_dependency = Depends(lambda: OpenAI())


@router.post("/", response_model=list[Product], status_code=status.HTTP_200_OK)
def generate_recommendations(
    shopping_cart: list[Product],
    collection_name: str = Query(
        "amazon_products", description="Qdrant collection containing products"
    ),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    qdrant_client: QdrantClient = qdrant_client_dependency,
    openai_client: OpenAI = openai_client_dependency,
) -> list[Product]:
    """Generate complementary product recommendations for a given shopping cart."""
    try:
        return recommend_products(
            qdrant_client=qdrant_client,
            openai_client=openai_client,
            collection_name=collection_name,
            shopping_cart=shopping_cart,
            limit=limit,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
