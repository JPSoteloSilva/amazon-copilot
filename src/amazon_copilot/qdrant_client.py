from fastembed import LateInteractionTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient as QdrantAPI
from qdrant_client import models
from qdrant_client.http.models import CollectionInfo

from amazon_copilot.schemas import Product, ProductResponse


class QdrantClient:
    """Client for interacting with the Qdrant vector database."""

    def __init__(
        self,
        host: str,
        port: int,
        dense_model_name: str,
        sparse_model_name: str,
        late_interaction_model_name: str,
    ) -> None:
        """Initialize the QdrantClient.

        Args:
            host: Qdrant server host.
            port: Qdrant server port.
            api_key: Qdrant API key.
            dense_embedding_name: Name of the dense embedding model.
            sparse_embedding_name: Name of the sparse embedding model.
            late_interaction_embedding_name: Name of the late interaction embedding
                model.
        """
        self.host = host
        self.port = port
        self.dense_model_name = dense_model_name
        self.sparse_model_name = sparse_model_name
        self.late_interaction_model_name = late_interaction_model_name

        self.sparse_model_field_name = self.sparse_model_name.split("/")[-1]
        self.dense_model_field_name = self.dense_model_name.split("/")[-1]
        self.late_interaction_model_field_name = self.late_interaction_model_name.split(
            "/"
        )[-1]

        list_of_dense_models = TextEmbedding.list_supported_models()
        list_of_late_interaction_models = (
            LateInteractionTextEmbedding.list_supported_models()
        )
        for model in list_of_dense_models:
            if model["model"] == self.dense_model_name:
                self.dense_model_dim = model["dim"]
        if self.dense_model_dim is None:
            raise ValueError(f"Dense model {self.dense_model_name} not found")

        for model in list_of_late_interaction_models:
            if model["model"] == self.late_interaction_model_name:
                self.late_interaction_model_dim = model["dim"]
        if self.late_interaction_model_dim is None:
            raise ValueError(
                f"Late interaction model {self.late_interaction_model_name} not found"
            )

        # Initialize the Qdrant client
        self.client = QdrantAPI(
            host=self.host,
            port=self.port,
        )

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
            self.late_interaction_model_field_name: models.VectorParams(
                size=self.late_interaction_model_dim,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM,
                ),
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
    ) -> int:
        """Add a batch of products to the specified collection.

        Args:
            products: List of products to add.
            collection_name: Name of the collection to add the products to.
            batch_size: Number of products to add in each batch.

        Returns:
            Number of products successfully added.
        """
        successful_adds = 0

        # Process products in batches
        for i in range(0, len(products), batch_size):
            batch = products[i : i + batch_size]
            points = []

            for product in batch:
                try:
                    # Add point to the batch
                    point = models.PointStruct(
                        id=product.id,
                        vector={
                            self.dense_model_field_name: models.Document(
                                text=product.name, model=self.dense_model_name
                            ),
                            self.sparse_model_field_name: models.Document(
                                text=product.name, model=self.sparse_model_name
                            ),
                            self.late_interaction_model_field_name: models.Document(
                                text=product.name,
                                model=self.late_interaction_model_name,
                            ),
                        },
                        payload=product.model_dump(),
                    )
                    points.append(point)
                    successful_adds += 1
                except Exception as e:
                    print(f"Failed to process product {product.id}: {e}")

            # Add batch to the collection
            if points:
                try:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=points,
                    )
                except Exception as e:
                    print(f"Failed to add batch: {e}")
                    successful_adds -= len(points)

        return successful_adds

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
    ) -> list[ProductResponse]:
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
        filters = []
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
            query_filter = models.Filter(must=filters)  # type: ignore
        else:
            query_filter = None

        prefetch = [
            models.Prefetch(
                query=models.Document(text=query, model=self.dense_model_name),
                using=self.dense_model_field_name,
                limit=prefetch_limit,
                filter=query_filter,
            ),
            models.Prefetch(
                query=models.Document(text=query, model=self.sparse_model_name),
                using=self.sparse_model_field_name,
                limit=prefetch_limit,
                filter=query_filter,
            ),
        ]

        # Execute search with reranking
        response = self.client.query_points(
            collection_name=collection_name,
            prefetch=prefetch,
            query=models.Document(text=query, model=self.late_interaction_model_name),
            using=self.late_interaction_model_field_name,
            with_vectors=with_vectors,
            with_payload=with_payload,
            limit=limit,
            offset=offset,
            query_filter=query_filter,
        )

        results = response.points
        if results is None:
            return []
        return [
            ProductResponse(
                payload=Product(**result.payload),  # type: ignore
                score=result.score,
            )
            for result in results
        ]

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
