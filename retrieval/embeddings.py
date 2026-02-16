from config.settings import EMBEDDING_MODEL_NAME
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-large")

    def embed_query(self, text: str):
        text = f"query: {text}"
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_passage(self, text: str):
        text = f"passage: {text}"
        return self.model.encode(text, normalize_embeddings=True).tolist()
