import os
from catalog.loader import load_catalog
from retrieval.embeddings import EmbeddingModel
from retrieval.vectorstore import PineconeVectorStore

def ingest():
    # --- Charger le catalogue ---
    products = load_catalog()
    if not products:
        print("⚠️ Aucun produit trouvé dans catalog.json")
        return

    # --- Initialiser embeddings ---
    embeddings_model = EmbeddingModel()
    
    # --- Créer PineconeVectorStore et recréer l'index propre ---
    store = PineconeVectorStore(recreate_index=True)

    # --- Préparer les vecteurs pour Pinecone ---
    vectors = []
    for product in products:
        # Texte combiné pour E5/BGE
        text = f"{product.name}. {product.description}. {product.category}"
        vector = embeddings_model.embed_passage(text)

        # Metadata complète + "type" pour filtrage Pinecone
        metadata = {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "description": product.description,
            "price": product.price,
            "currency": product.currency,
            "in_stock": product.in_stock,
            "stock_quantity": product.stock_quantity,
            "image_url": product.image_url,
            "type": "product"  # ✅ indispensable
        }

        # Construire le dictionnaire pour Pinecone
        vectors.append({
            "id": str(product.id),
            "values": vector,
            "metadata": metadata
        })

    # --- Injection dans Pinecone ---
    store.upsert(vectors)
    print(f"✅ {len(vectors)} produits indexés dans Pinecone.")

if __name__ == "__main__":
    ingest()
