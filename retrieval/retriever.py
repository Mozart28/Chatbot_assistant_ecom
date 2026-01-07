
from typing import List
from retrieval.embeddings import get_embeddings
from retrieval.vectorstore import PineconeVectorStore
from catalog.schema import Product
from catalog.validator import filter_available_products


class ProductRetriever:
    def __init__(self, top_k: int = 5):
        self.embeddings = get_embeddings()
        self.store = PineconeVectorStore()
        self.top_k = top_k

    def search(self, query: str) -> List[Product]:
        vector = self.embeddings.embed_query(query)

        results = self.store.query(
            vector=vector,
            top_k=self.top_k
        )

        products = [
            Product(**match["metadata"])
            for match in results["matches"]
        ]

        return filter_available_products(products)
