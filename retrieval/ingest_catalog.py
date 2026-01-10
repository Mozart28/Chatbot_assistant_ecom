import os
from catalog.loader import load_catalog
from retrieval.embeddings import get_embeddings
from retrieval.vectorstore import PineconeVectorStore

def ingest():
    # --- Charger le catalogue ---
    products = load_catalog()
    if not products:
        print("⚠️ Aucun produit trouvé dans catalog.json")
        return

    # --- Initialiser embeddings ---
    embeddings_model = get_embeddings()
    
    # --- Créer PineconeVectorStore et recréer l'index propre ---
    store = PineconeVectorStore(recreate_index=True)

    # --- Préparer les vecteurs pour Pinecone ---
    vectors = []
    for product in products:
        # Combinaison texte pour embeddings
        text = f"{product.name}. {product.description}. {product.category}"
        vector = embeddings_model.embed_query(text)


        
   

        # Construire le dictionnaire conforme Pinecone v8
        vectors.append({
            "id": str(product.id),
            "values": vector,
            "metadata": {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "description": product.description,
                "price": product.price,
                "currency": product.currency,
                "in_stock": product.in_stock,
                "stock_quantity": product.stock_quantity,
                
            }
        })

    # --- Injection dans Pinecone ---
    store.upsert(vectors)
    print(f"✅ {len(vectors)} produits indexés dans Pinecone.")

if __name__ == "__main__":
    ingest()
