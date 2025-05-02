# %%
import start_research
# %%
#  correr 'docker-compose up -d qdrant' en la terminal
# %%
from amazon_copilot import QdrantClient
# %%

client = QdrantClient(
    host="localhost",
    port=6333,
    dense_model_name="sentence-transformers/all-MiniLM-L6-v2",
    sparse_model_name="Qdrant/bm25",
    late_interaction_model_name="colbert-ir/colbertv2.0",
)
# %%
client.create_collection("test")
# %%
from amazon_copilot.utils import load_data

products = load_data("data/Amazon-Products.csv", nrows=100)  # hay algun error para todos los datos
products
# %%
client.add_products(
    products=products,
    collection_name="test",
)
# %%
client.search_similar_products(
    query="air conditioner",
    collection_name="test",
)
# %%
client.delete_collection("test")
# %%
