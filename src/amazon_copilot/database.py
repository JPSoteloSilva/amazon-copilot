"""Database service for the Amazon Copilot application."""

import uuid
from typing import Any, cast

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer

from amazon_copilot.config import settings
from amazon_copilot.models import AmazonProduct, ProductEmbedding


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self) -> None:
        """Initialize the Qdrant service."""
        # Connect to Qdrant
        self.client = QdrantClient(
            host=settings.qdrant.host,
            port=settings.qdrant.port,
        )

        # Initialize the embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Ensure collection exists
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self) -> None:
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if settings.qdrant.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=settings.qdrant.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=settings.qdrant.vector_size,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a text using the embedding model.

        Args:
            text: The text to generate an embedding for

        Returns:
            The embedding as a list of floats
        """
        # The encode method has complex return types, but we'll specify parameters
        # to ensure we get a numpy array with normalize_embeddings=True
        embedding_array = self.model.encode(  # type: ignore
            text, convert_to_numpy=True, normalize_embeddings=True
        )

        # Convert numpy array to list of floats
        # We know it's an ndarray because of convert_to_numpy=True
        float_list = embedding_array.tolist()  # type: ignore

        # Convert all elements to float to ensure type safety
        return [float(val) for val in float_list]

    def add_product(self, product: AmazonProduct) -> None:
        """Add a product to the database with its embedding.

        Args:
            product: The product to add
        """
        # Generate embedding for the product name
        embedding = self.generate_embedding(product.name)

        # Create a UUID for the point (Qdrant accepts UUIDs)
        point_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"product-{product.id}")

        # Add to Qdrant
        try:
            self.client.upsert(
                collection_name=settings.qdrant.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=str(point_id),  # Convert UUID to string
                        vector=embedding,
                        payload=product.model_dump(),
                    )
                ],
            )
        except Exception as e:
            # Provide more detailed error information
            raise Exception(f"Failed to add product {product.id}: {str(e)}") from e

    def search_similar_products(
        self, query: str, limit: int = 10
    ) -> list[ProductEmbedding]:
        """Search for products similar to a query.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            List of products with their embeddings, sorted by relevance
        """
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)

        # Search in Qdrant
        search_result = self.client.search(
            collection_name=settings.qdrant.collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_vectors=True,  # Include vectors in the response
        )

        # Convert results to our model
        results: list[ProductEmbedding] = []

        for scored_point in search_result:
            try:
                # Skip points without payload
                if not scored_point.payload:
                    continue

                # Convert payload to AmazonProduct
                product = AmazonProduct.model_validate(scored_point.payload)

                # Default to query embedding
                embedding_vector: list[float] = query_embedding

                # Try to extract vector from the search result
                if scored_point.vector is not None:
                    if isinstance(scored_point.vector, np.ndarray):
                        # For numpy arrays
                        numpy_vec = cast(Any, scored_point.vector)  # type: ignore
                        embedding_vector = [float(x) for x in numpy_vec.tolist()]  # type: ignore
                    elif isinstance(scored_point.vector, list):
                        # For list values, ensure all elements are float
                        vector_list = cast(list[Any], scored_point.vector)
                        embedding_vector = [float(val) for val in vector_list]

                # Add to results
                results.append(
                    ProductEmbedding(
                        product=product,
                        embedding=embedding_vector,
                    )
                )
            except Exception as e:
                # Skip problematic entries but log the error
                print(f"Error processing search result: {str(e)}")
                continue

        return results
