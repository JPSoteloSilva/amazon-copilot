# %%
import start_research

# %%
from fastembed import TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding

dense_embedding_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
bm25_embedding_model = SparseTextEmbedding("Qdrant/bm25")
late_interaction_embedding_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")


# %%
dense_embedding_model.model.__dict__
# %%
text = "This is a test by friend, how are you?. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
text = "This is an apple"
# %%
dense_embedding = list(dense_embedding_model.embed(text))[0].tolist()
dense_embedding
# %%
sparse_embedding = list(bm25_embedding_model.embed(text))[0]
sparse_embedding
# %%
late_interaction_embedding = list(late_interaction_embedding_model.embed(text))[0]
late_interaction_embedding.shape
# %%
late_interaction_embedding.tolist()

# %%
len(late_interaction_embedding)
# %%
len(late_interaction_embedding[0])

# %%
