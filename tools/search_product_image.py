from retrieval.retriever import ProductRetriever
from catalog.schema import Product
import streamlit as st

retriever = ProductRetriever(top_k=10)

@st.cache_data
def search_product_image(user_input: str):
    products = retriever.search(user_input)
    
    # 1️⃣ Vector search
    for product in products:
        product_dict = product.__dict__
        image_url = product_dict.get("image_url")
        if image_url:
            return {
                "id": product_dict["id"],
                "name": product_dict["name"],
                "category": product_dict.get("category"),
                "price": product_dict.get("price"),
                "in_stock": product_dict.get("in_stock", False),
                "image_url": image_url
            }

    # 2️⃣ Fallback keyword (plus permissif)
    query_words = [w.lower() for w in user_input.split() if len(w) > 2]
    for product in products:
        product_dict = product.__dict__
        name_lower = product_dict.get("name", "").lower()
        # Permissif : match n'importe quel mot
        if any(word in name_lower for word in query_words):
            image_url = product_dict.get("image_url")
            if image_url:
                return {
                    "id": product_dict["id"],
                    "name": product_dict["name"],
                    "category": product_dict.get("category"),
                    "price": product_dict.get("price"),
                    "in_stock": product_dict.get("in_stock", False),
                    "image_url": image_url
                }

    return None
