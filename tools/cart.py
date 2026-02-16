import streamlit as st





def add_product_to_cart(product):
    if not product:
        return "❌ Impossible d’ajouter le produit au panier."

    st.session_state.cart.append({
        "id": product["id"],
        "name": product["name"],
        "price": product["price"]
    })

    return f"✅ **{product['name']}** ajouté au panier."

