
def route_intent(user_input: str) -> str:
    text = user_input.lower()

    keywords = [
        "acheter", "prix", "commande", "produit",
        "disponible", "recommande", "cherche","vendez-vous",
        "avez-vous"
    ]

    if any(k in text for k in keywords):
        return "product_search"

    return "fallback"
