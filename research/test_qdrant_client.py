# %%
import start_research
# %%
#  correr 'docker-compose up -d qdrant' en la terminal
# %%
from amazon_copilot.qdrant_client import QdrantClient
# %%

client = QdrantClient(
    host="localhost",
    port=6333,
    dense_model_name="sentence-transformers/all-MiniLM-L6-v2",
    sparse_model_name="Qdrant/bm25",
)
# %%
client.create_collection("test_2")
# %%
from amazon_copilot.utils import load_data

products = load_data("data/Amazon-Products.csv", nrows=100)  # hay algun error para todos los datos
products
# %%
client.add_products(
    products=products,
    collection_name="test_2",
)
# %%
client.search_similar_products(
    query="air conditioner",
    collection_name="test_2",
)

# %%
client.search_similar_products(
    query="air conditioner",
    collection_name="test_2",
    main_category="appliances",
    sub_category="Air Conditioners",
)
# %%
client.list_products(
    collection_name="test_2",
)
# %%
client.delete_collection("test_2")
# %%
