"""Models for the Amazon Copilot application."""

from pydantic import BaseModel, Field


class AmazonProduct(BaseModel):
    """Model for an Amazon product."""

    id: str = Field(description="Product ID")
    name: str = Field(description="Product name")
    main_category: str = Field(description="Main product category")
    sub_category: str = Field(description="Product sub-category")
    image: str = Field(description="URL to product image")
    link: str = Field(description="URL to product page")
    ratings: float | None = Field(None, description="Product rating (0-5)")
    no_of_ratings: str | None = Field(None, description="Number of ratings")
    discount_price: str | None = Field(None, description="Discounted price")
    actual_price: str | None = Field(None, description="Original price")


class ProductEmbedding(BaseModel):
    """Model for a product with embedding vector."""

    product: AmazonProduct = Field(description="The Amazon product")
    embedding: list[float] = Field(description="Embedding vector of the product name")
