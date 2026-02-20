
def add_product_to_cart(product):
    """
    Add product to cart and suggest contacting agent
    
    Returns:
        dict: Success message + contact suggestion
    """
    if not product:
        return {
            "success": False,
            "error": "❌ Impossible d'ajouter le produit au panier."
        }
    
    # Add to cart (your existing logic)
    # st.session_state.cart.append({
    #     "id": product["id"],
    #     "name": product["name"],
    #     "price": product["price"]
    # })
    
    # Return success + contact suggestion
    return {
        "success": True,
        "product_added": product["name"],
        "message": f"✅ **{product['name']}** ajouté au panier.",
        "suggest_contact": True,  # Flag to suggest contact
        "contact_question": "Voulez-vous que je vous donne le numéro d'un commercial pour bloquer votre commande ?"
    }