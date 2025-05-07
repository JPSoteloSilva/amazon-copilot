from fastapi import APIRouter, Depends, Query

from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import Product
from amazon_copilot.services.products import (
    add_products,
    delete_product,
    get_product,
    list_products,
    search_products,
)
from amazon_copilot.utils import get_qdrant_client

router = APIRouter(prefix="/products", tags=["products"])

# Module-level singleton for dependency
qdrant_client_dependency = Depends(get_qdrant_client)


@router.get("/", response_model=list[Product])
def list_products_api(
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to retrieve products from",
    ),
    limit: int = Query(
        10, description="Maximum number of products to retrieve", ge=1, le=100
    ),
    offset: int = Query(0, description="Number of products to skip", ge=0),
    client: QdrantClient = qdrant_client_dependency,
) -> list[Product]:
    return list_products(
        client=client, collection_name=collection_name, limit=limit, offset=offset
    )


@router.get("/search", response_model=list[Product])
def search_products_api(
    query: str,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to search products in",
    ),
    limit: int = Query(10, description="Maximum number of products to return"),
    offset: int = Query(0, description="Number of products to skip"),
    main_category: str | None = Query(
        None, description="Main category to filter products by"
    ),
    sub_category: str | None = Query(
        None, description="Sub category to filter products by"
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> list[Product]:
    return search_products(
        client=client,
        query=query,
        collection_name=collection_name,
        limit=limit,
        offset=offset,
        main_category=main_category,
        sub_category=sub_category,
    )


@router.post("/", response_model=int)
def add_product(
    product: Product,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to add product to",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> int:
    return add_products(
        client=client, collection_name=collection_name, products=[product]
    )


@router.get("/{product_id}", response_model=Product)
def get_product_api(
    product_id: int,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to retrieve the product from",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> Product:
    return get_product(
        client=client, collection_name=collection_name, product_id=product_id
    )


@router.delete("/{product_id}", response_model=bool)
def delete_product_api(
    product_id: int,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to delete product from",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> bool:
    return delete_product(
        client=client, collection_name=collection_name, product_id=product_id
    )
