from fastapi import APIRouter, Depends, HTTPException, Query

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


@router.post("/", response_model=tuple[list[Product], dict[int, str]])
def add_product(
    product: Product,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to add product to",
    ),
    prevent_duplicates: bool = Query(
        True,
        description="Whether to prevent adding products with IDs that already exist",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> tuple[list[Product], dict[int, str]]:
    successful_products, failed_products = add_products(
        client=client,
        collection_name=collection_name,
        products=[product],
        prevent_duplicates=prevent_duplicates,
    )

    # If the product failed due to duplication
    if (
        product.id in failed_products
        and "already exists" in failed_products[product.id]
    ):
        raise HTTPException(
            status_code=409,  # Conflict status code
            detail={
                "message": f"Product with ID {product.id} already exists",
                "product_id": product.id,
                "error": failed_products[product.id],
            },
        )

    # If it failed for any other reason
    if not successful_products and failed_products:
        raise HTTPException(
            status_code=400,  # Bad Request status code
            detail={
                "message": "Failed to add product",
                "product_id": product.id,
                "error": failed_products.get(product.id, "Unknown error"),
            },
        )

    return successful_products, failed_products


@router.get("/{product_id}", response_model=Product)
def get_product_api(
    product_id: int,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to retrieve the product from",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> Product:
    try:
        return get_product(
            client=client, collection_name=collection_name, product_id=product_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{product_id}")
def delete_product_api(
    product_id: int,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to delete product from",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> dict[str, bool]:
    try:
        delete_product(
            client=client, collection_name=collection_name, product_id=product_id
        )
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
