# %%
"""Quick interactive test of the recommendation pipeline.

Prerequisites:
1. Run `docker-compose up -d qdrant` so the vector DB is available on localhost:6333.
2. Set the environment variable `OPENAI_API_KEY` with a valid key.
"""
# %% Imports
from openai import OpenAI

from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.utils import load_data
from amazon_copilot.services.ai.recommendation.main import recommend_products
import random
import start_research

# %% Initialise clients
qdrant_client = QdrantClient(
    host="localhost",
    port=6333,
    dense_model_name="sentence-transformers/all-MiniLM-L6-v2",
    sparse_model_name="Qdrant/bm25",
)
openai_client = OpenAI()

# %% Create collection & ingest sample products
collection_name = "recommendation_test"
qdrant_client.create_collection(collection_name)

# %%
products = load_data("data/Amazon-Products.csv", nrows=10000)
_ = qdrant_client.add_products(products, collection_name)

# %% Build a fake shopping cart (4 random products)
shopping_cart = random.sample(products, k=4)
print("Cart:")
for p in shopping_cart:
    print(f"- {p.name} (id={p.id})")

# %% Get recommendations
recs = recommend_products(
    qdrant_client=qdrant_client,
    openai_client=openai_client,
    collection_name=collection_name,
    shopping_cart=shopping_cart,
    limit=10,
)

print("\nRecommended products:")
for r in recs:
    print(f"* {r.name} (id={r.id})")

# %% Clean-up (optional)
qdrant_client.delete_collection(collection_name)
# qdrant_client.close() 
# %%
