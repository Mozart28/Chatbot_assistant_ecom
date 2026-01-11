from retrieval.retriever import ProductRetriever

retriever = ProductRetriever()

def search_product_image(user_input: str):
    products = retriever.search(user_input)  # renvoie une liste de Product ou dicts

    if not products:
        return None

    # prends le premier produit trouvé
    product = products[0]

    # Assure-toi que product est un dict (ou converti depuis Product)
    if hasattr(product, "__dict__"):  # si c'est un dataclass Product
        product = product.__dict__

    # Vérifie image_url
    if not product.get("image_url"):
        return None

    return {
        "id": product["id"],
        "name": product["name"],
        "category": product["category"],
        "price": product.get("price"),
        "in_stock": product.get("in_stock", False),
        "image_url": product["image_url"]
    }
