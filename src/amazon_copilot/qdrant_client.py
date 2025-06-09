from typing import cast

from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient as QdrantAPI
from qdrant_client.http import models
from qdrant_client.http.models import CollectionInfo
from tqdm import tqdm

from amazon_copilot.schemas import Product


class QdrantClient:
    """Client for interacting with the Qdrant vector database."""

    def __init__(
        self,
        host: str,
        port: int,
        dense_model_name: str,
        sparse_model_name: str,
    ) -> None:
        """Initialize the QdrantClient.

        Args:
            host: Qdrant server host.
            port: Qdrant server port.
            dense_embedding_name: Name of the dense embedding model.
            sparse_embedding_name: Name of the sparse embedding model.
        """
        self.dense_model_name = dense_model_name
        self.sparse_model_name = sparse_model_name

        self.dense_embedder = TextEmbedding(self.dense_model_name)
        self.sparse_embedder = SparseTextEmbedding(self.sparse_model_name)

        self.sparse_model_field_name = self.sparse_model_name.split("/")[-1]
        self.dense_model_field_name = self.dense_model_name.split("/")[-1]

        list_of_dense_models = TextEmbedding.list_supported_models()
        for model in list_of_dense_models:
            if model["model"] == self.dense_model_name:
                self.dense_model_dim = model["dim"]
        if self.dense_model_dim is None:
            raise ValueError(f"Dense model {self.dense_model_name} not found")

        # Initialize the Qdrant client
        self.client = QdrantAPI(
            host=host,
            port=port,
        )

    def close(self) -> None:
        """Close the Qdrant client."""
        self.client.close()

    def create_collection(
        self,
        collection_name: str,
    ) -> bool:
        """Create a new collection in the Qdrant database.

        Args:
            collection_name: Name of the collection to create.

        Returns:
            True if the collection was created successfully.
        """

        vectors_config = {
            self.dense_model_field_name: models.VectorParams(
                size=self.dense_model_dim,
                distance=models.Distance.COSINE,
            ),
        }

        sparse_vectors_config = {
            self.sparse_model_field_name: models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            ),
        }

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=vectors_config,
                sparse_vectors_config=sparse_vectors_config,
            )
            return True
        except Exception as e:
            print(f"Failed to create collection: {e}")
            return False

    def add_products(
        self,
        products: list[Product],
        collection_name: str,
        batch_size: int = 100,
        prevent_duplicates: bool = True,
    ) -> tuple[list[Product], dict[int, str]]:
        """Add a batch of products to the specified collection.

        Args:
            products: List of products to add.
            collection_name: Name of the collection to add the products to.
            batch_size: Number of products to add in each batch.
            prevent_duplicates: If True, checks for existing products with the same ID
                and prevents overwriting.

        Returns:
            A tuple containing:
            - List of products that were successfully added
            - Dictionary mapping failed product IDs to failure reasons
        """
        successful_products: list[Product] = []
        failed_products: dict[int, str] = {}

        # Check for existing products if duplicate prevention is enabled
        if prevent_duplicates and products:
            for product in products:
                try:
                    # Try to retrieve the product to check if it exists
                    response = self.client.retrieve(
                        collection_name=collection_name,
                        ids=[product.id],
                        with_payload=False,
                    )
                    # Check if response is not empty (product exists)
                    if response:
                        failed_products[product.id] = (
                            f"Product with ID {product.id} already exists"
                        )
                except Exception:
                    # If there's an error (like collection doesn't exist), skip check
                    pass

            # Filter out products that already exist
            products_to_add = [p for p in products if p.id not in failed_products]
            if not products_to_add:
                return successful_products, failed_products
        else:
            products_to_add = products

        for i in tqdm(range(0, len(products_to_add), batch_size)):
            batch = products_to_add[i : i + batch_size]
            names = [p.name for p in batch]

            try:
                dense_vecs = list(self.dense_embedder.embed(names))
                sparse_vecs = list(self.sparse_embedder.embed(names))
            except Exception as e:
                # If embedding fails for the entire batch, mark all as failed
                error_message = f"Embedding generation failed: {str(e)}"
                for product in batch:
                    failed_products[product.id] = error_message
                continue

            points = []
            # Track products and their points for error reporting
            batch_product_map: dict[int, Product] = {}

            try:
                for product, dense_vec, sparse_vec in zip(
                    batch, dense_vecs, sparse_vecs, strict=True
                ):
                    points.append(
                        models.PointStruct(
                            id=product.id,
                            vector={
                                self.dense_model_field_name: cast(
                                    list[float], dense_vec.tolist()
                                ),
                                self.sparse_model_field_name: sparse_vec.as_object(),  # type: ignore
                            },
                            payload=product.model_dump(),
                        )
                    )
                    batch_product_map[product.id] = product
            except Exception as e:
                # If point construction fails, mark affected products as failed
                error_message = f"Point construction failed: {str(e)}"
                for product in batch:
                    failed_products[product.id] = error_message
                continue

            try:
                self.client.upsert(collection_name=collection_name, points=points)
                # Mark all products in this batch as successful
                for product in batch:
                    successful_products.append(product)
            except Exception as e:
                error_message = f"Upsert operation failed: {str(e)}"
                # Mark all products in this batch as failed
                for product in batch:
                    failed_products[product.id] = error_message

        return successful_products, failed_products

    def search_similar_products(
        self,
        query: str,
        collection_name: str,
        main_category: str | None = None,
        sub_category: str | None = None,
        limit: int = 10,
        offset: int = 0,
        prefetch_limit: int = 20,
        with_vectors: bool = False,
        with_payload: bool = True,
    ) -> list[Product]:
        """Search for products similar to the query using hybrid search with reranking.

        This implementation follows the two-stage approach:
        1. First retrieval: Use prefetch with dense and sparse vectors to get candidates
        2. Reranking: Use late interaction model to rerank the candidates

        Args:
            query: The search query.
            collection_name: Name of the collection to search in.
            main_category: Filter by main category if provided.
            sub_category: Filter by sub category if provided.
            limit: Maximum number of results to return.
            offset: Offset for pagination.
            prefetch_limit: Maximum number of results to return from prefetch.
            with_vectors: Whether to return vectors.
            with_payload: Whether to return payload.

        Returns:
            Dictionary with results and pagination information.
        """
        # Prepare filter if categories are specified
        filters: list[models.Condition] = []
        if main_category:
            filters.append(
                models.FieldCondition(
                    key="main_category",
                    match=models.MatchText(text=main_category),
                )
            )

        if sub_category:
            filters.append(
                models.FieldCondition(
                    key="sub_category",
                    match=models.MatchText(text=sub_category),
                )
            )

        if filters:
            query_filter = models.Filter(must=filters)
        else:
            query_filter = None

        # Generate embeddings for the query
        dense_embedding_iter = iter(self.dense_embedder.query_embed(query))
        try:
            dense_vectors = next(dense_embedding_iter).tolist()
        except StopIteration as e:
            raise ValueError(
                "Dense embedding generation failed: ",
                "no embeddings returned for the query.",
            ) from e

        sparse_embedding_iter = iter(self.sparse_embedder.query_embed(query))
        try:
            sparse_vectors = next(sparse_embedding_iter).as_object()
        except StopIteration as e:
            raise ValueError(
                "Sparse embedding generation failed: ",
                "no embeddings returned for the query.",
            ) from e
        prefetch = [
            models.Prefetch(
                query=dense_vectors,  # type: ignore
                using=self.dense_model_field_name,
                limit=prefetch_limit,
                filter=query_filter,
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=list(sparse_vectors["indices"]),
                    values=list(sparse_vectors["values"]),
                ),
                using=self.sparse_model_field_name,
                limit=prefetch_limit,
                filter=query_filter,
            ),
        ]

        # Execute search with reranking
        response = self.client.query_points(
            collection_name=collection_name,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            with_vectors=with_vectors,
            with_payload=with_payload,
            limit=limit,
            offset=offset,
            query_filter=query_filter,
        )

        if response.points is None:
            return []
        else:
            results: list[Product] = []
            for point in response.points:
                if point.payload is None:
                    continue
                results.append(
                    Product(
                        id=int(point.id),
                        name=point.payload["name"],
                        main_category=point.payload["main_category"],
                        sub_category=point.payload["sub_category"],
                        image=point.payload["image"],
                        link=point.payload["link"],
                        ratings=point.payload["ratings"],
                        no_of_ratings=point.payload["no_of_ratings"],
                        discount_price=point.payload["discount_price"],
                        actual_price=point.payload["actual_price"],
                    )
                )
            return results

    def get_collection_info(self, collection_name: str) -> CollectionInfo:
        """Get information about a collection.

        Args:
            collection_name: Name of the collection.

        Returns:
            Dictionary containing collection information.
        """
        try:
            return self.client.get_collection(collection_name)

        except Exception as e:
            raise e

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection.

        Args:
            collection_name: Name of the collection to delete.

        Returns:
            True if the collection was deleted successfully.
        """
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception as e:
            print(f"Failed to delete collection: {e}")
            return False

    def list_products(
        self,
        collection_name: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Product]:
        """List products from the collection.

        Args:
            collection_name: Name of the collection to list products from.
            limit: Maximum number of products to return.
            offset: Number of products to skip.

        Returns:
            List of Product objects.
        """
        response = self.client.scroll(
            collection_name=collection_name,
            limit=limit,
            offset=offset,
        )
        results: list[Product] = []
        for record in response[0]:
            if record.payload is None:
                continue
            results.append(Product(**record.payload))
        return results

    def get_product(self, collection_name: str, product_id: int) -> Product:
        """Get a product from the collection.

        Args:
            collection_name: Name of the collection to get the product from.
            product_id: ID of the product to get.

        Returns:
            Product object.

        Raises:
            ValueError: If the product with the specified ID is not found.
        """
        response = self.client.retrieve(
            collection_name=collection_name,
            ids=[product_id],
            with_payload=True,
            with_vectors=False,
        )

        # Check if response is empty
        if not response:
            raise ValueError(f"Product with id {product_id} not found")

        # Check if the product has a payload
        if response[0].payload is None:
            raise ValueError(f"Product with id {product_id} found but has no payload")

        return Product(**response[0].payload)

    def delete_product(self, collection_name: str, product_id: int) -> None:
        """Delete a product from the collection.

        Args:
            collection_name: Name of the collection to delete the product from.
            product_id: ID of the product to delete.

        Raises:
            Exception: If the product is not found or the deletion fails.
        """
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.Filter(
                    must=[models.HasIdCondition(has_id=[product_id])]
                ),
            )
        except Exception as e:
            raise e
