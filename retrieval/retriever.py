from typing import List, Union, Dict
from retrieval.embeddings import EmbeddingModel
from retrieval.vectorstore import PineconeVectorStore
from catalog.schema import Product
from catalog.validator import filter_available_products


class ProductRetriever:
    def __init__(self, top_k: int = 3, score_threshold: float = 0.3):
        self.embeddings = EmbeddingModel()
        self.store = PineconeVectorStore()
        self.top_k = top_k
        self.score_threshold = score_threshold

    def search(self, query: str, intent: str | None = None) -> List[Union[Product, Dict]]:
        """
        Search for both products AND PDF documents
        Returns a mix of Product objects and dict for PDF documents
        """
        # Enrichir la requête pour E5
        enriched_query = (
            f"Intent: {intent}. {query}" if intent else query
        )

        vector = self.embeddings.embed_query(enriched_query)

        # ✅ FIXED: Search BOTH products AND PDF documents
        results = self.store.query(
            vector=vector,
            top_k=self.top_k * 2,  # Get more results to include both types
            filter={"type": {"$in": ["product", "pdf_document"]}}  # ← INCLUDE BOTH!
        )

        items = []
        
        for match in results.get("matches", []):
            metadata = match["metadata"].copy()
            item_type = metadata.get("type")
            
            if item_type == "product":
                # Convert to Product object
                metadata.pop("type", None)
                try:
                    product = Product(**metadata)
                    items.append(product)
                except Exception as e:
                    print(f"⚠️  Could not parse product: {e}")
            
            elif item_type == "pdf_document":
                # Keep as dict with all metadata
                items.append({
                    "type": "pdf_document",
                    "text": metadata.get("text", ""),
                    "filename": metadata.get("filename", ""),
                    "document_id": metadata.get("document_id", ""),
                    "score": match.get("score", 0)
                })

        # Filter only available products (not PDFs)
        products_only = [item for item in items if isinstance(item, Product)]
        filtered_products = filter_available_products(products_only)
        
        # Combine filtered products with PDF documents
        pdf_docs = [item for item in items if isinstance(item, dict)]
        
        # Return products first, then PDFs
        return filtered_products + pdf_docs
