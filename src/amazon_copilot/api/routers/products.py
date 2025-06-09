from fastapi import APIRouter, Depends, HTTPException, Query, status

from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import AddProductsResponse, DeleteResponse, Product
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


@router.get("/", response_model=list[Product], status_code=status.HTTP_200_OK)
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
    try:
        return list_products(
            client=client, collection_name=collection_name, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}",
        ) from e


@router.get("/search", response_model=list[Product], status_code=status.HTTP_200_OK)
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
    price_min: float | None = Query(
        None,
        description="Minimum price filter (in USD)",
        ge=0,
    ),
    price_max: float | None = Query(
        None,
        description="Maximum price filter (in USD)",
        ge=0,
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> list[Product]:
    try:
        return search_products(
            client=client,
            query=query,
            collection_name=collection_name,
            limit=limit,
            offset=offset,
            main_category=main_category,
            sub_category=sub_category,
            price_min=price_min,
            price_max=price_max,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search products: {str(e)}",
        ) from e


@router.post(
    "/", response_model=AddProductsResponse, status_code=status.HTTP_201_CREATED
)
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
) -> AddProductsResponse:
    try:
        response = add_products(
            client=client,
            collection_name=collection_name,
            products=[product],
            prevent_duplicates=prevent_duplicates,
        )

        # If the product failed due to duplication
        if (
            product.id in response.failed
            and "already exists" in response.failed[product.id]
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"Product with ID {product.id} already exists",
                    "product_id": product.id,
                    "error": response.failed[product.id],
                },
            )

        # If it failed for any other reason
        if not response.successful and response.failed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Failed to add product",
                    "product_id": product.id,
                    "error": response.failed.get(product.id, "Unknown error"),
                },
            )

        return response
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while adding product: {str(e)}",
        ) from e


@router.get("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product: {str(e)}",
        ) from e


@router.delete(
    "/{product_id}", response_model=DeleteResponse, status_code=status.HTTP_200_OK
)
def delete_product_api(
    product_id: int,
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to delete product from",
    ),
    client: QdrantClient = qdrant_client_dependency,
) -> DeleteResponse:
    try:
        delete_product(
            client=client, collection_name=collection_name, product_id=product_id
        )
        return DeleteResponse(
            success=True, message=f"Product {product_id} deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}",
        ) from e
