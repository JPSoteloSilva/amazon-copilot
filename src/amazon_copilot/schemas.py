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


class AddProductsResponse(BaseModel):
    """Response model for adding products with detailed success/failure information."""

    successful: list[Product]
    """List of products that were successfully added to the collection."""

    failed: dict[int, str]
    """Dictionary mapping failed product IDs to their error messages."""

    class Config:
        json_schema_extra = {
            "example": {
                "successful": [
                    {
                        "id": 1,
                        "name": "Sample Product",
                        "main_category": "Electronics",
                        "sub_category": "Phones",
                        "image": "https://example.com/image.jpg",
                        "link": "https://example.com/product",
                        "ratings": 4.5,
                        "no_of_ratings": 100,
                        "discount_price": 99.99,
                        "actual_price": 129.99,
                    }
                ],
                "failed": {
                    2: "Product with ID 2 already exists",
                    3: "Embedding generation failed: Invalid product name",
                },
            }
        }


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool
    """Whether the delete operation was successful."""

    message: str
    """Message describing the result of the operation."""

    class Config:
        json_schema_extra = {
            "example": {"success": True, "message": "Product deleted successfully"}
        }


class ProductQuery(BaseModel):
    query: str | None = None
    main_category: str | None = None
    price_min: float | None = None
    price_max: float | None = None


class AgentResponse(BaseModel):
    message: str
    preferences: ProductQuery


class QuestionsResponse(BaseModel):
    message: str
    restart: bool = False


class PresentationResponse(BaseModel):
    message: str
    products: list[Product]


class Message(BaseModel):
    role: str
    content: str
