from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from config.settings import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    EMBEDDING_MODEL_NAME
)

# Init Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Modèle d'embedding (le MÊME que l'ingestion)
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Texte réel
query_text = "casquette sport respirante"
vector = model.encode(query_text).tolist()

# Query Pinecone
res = index.query(
    vector=vector,
    top_k=5,
    include_metadata=True
)

print("=== PINECONE QUERY RESULTS ===")
for match in res["matches"]:
    print("ID:", match["id"])
    print("SCORE:", match["score"])
    print("METADATA:", match["metadata"])
    print("-" * 60)
