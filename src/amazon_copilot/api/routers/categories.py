from fastapi import APIRouter, HTTPException, Query, status

from amazon_copilot.services.categories import list_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=dict[str, list[str]], status_code=status.HTTP_200_OK)
def list_categories_api(
    collection_name: str = Query(
        "amazon_products",
        description="Name of the collection to get categories from",
    ),
) -> dict[str, list[str]]:
    """Get all main categories and their respective sub-categories.

    Returns a dictionary where keys are main categories and values are lists of
    sub-categories.
    Format: {"main_category": ["sub_category1", "sub_category2", ...]}

    This endpoint is useful for building category filters and navigation menus.
    """
    try:
        return list_categories(collection_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}",
        ) from e
