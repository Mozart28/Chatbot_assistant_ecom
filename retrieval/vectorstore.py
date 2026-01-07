from pinecone import Pinecone, ServerlessSpec
from config.settings import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EMBEDDING_DIMENSION,
)


class PineconeVectorStore:
    def __init__(self, recreate_index=False):
        """
        recreate_index=True => supprime l'ancien index et recrée un index propre
        """
        self.pc = Pinecone(api_key=PINECONE_API_KEY)

        if recreate_index and PINECONE_INDEX_NAME in self.pc.list_indexes().names():
            self.pc.delete_index(PINECONE_INDEX_NAME)

        self.index = self._get_or_create_index()

    def _get_or_create_index(self):
        existing = self.pc.list_indexes().names()

        if PINECONE_INDEX_NAME not in existing:
            self.pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION,
                ),
            )

        return self.pc.Index(PINECONE_INDEX_NAME)

    def upsert(self, vectors):
        """
        vectors = [
            {
                "id": str,
                "values": [...],
                "metadata": {...}
            }
        ]
        """
        # Vérification rapide pour debug
        if not vectors:
            print("⚠️ Aucun vecteur à upserter !")
            return

        self.index.upsert(vectors=vectors)
        print(f"✅ {len(vectors)} vecteurs upsertés dans Pinecone.")

    def query(self, vector, top_k=5, filter=None):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter,
        )
