
def search_product_image(user_input: str):
    product = search_products(user_input)  # ton RAG Pinecone

    if not product:
        return None

    if isinstance(product, list):
        product = product[0]  # meilleur match

    image_url = product.get("image_url")

    if not image_url:
        return None

    return {
        "name": product["name"],
        "image_url": image_url,
        "price": product.get("price"),
        "in_stock": product.get("in_stock", False)
    }
