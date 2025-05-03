from fastapi import APIRouter

from amazon_copilot.api.crud.products import get_product, list_products
from amazon_copilot.shared.schemas import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[Product])
def list_products_api():
    return list_products()


@router.get("/{product_id}", response_model=Product)
def get_product_api(product_id: int):
    return get_product(product_id)
