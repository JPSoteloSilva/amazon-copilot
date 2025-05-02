from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    main_category: str | None
    sub_category: str | None
    image: str
    link: str | None
    ratings: float | None
    no_of_ratings: int | None
    discount_price: float | None
    actual_price: float | None


class ProductResponse(BaseModel):
    payload: Product
    score: float
