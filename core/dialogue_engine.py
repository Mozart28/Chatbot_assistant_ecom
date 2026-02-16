
# core/dialogue_engine.py

from core.intents import detect_intent

def handle_pending_choice(state, user_input):
    if not state.pending_choice:
        return None

    intent = detect_intent(user_input)

    if intent == "UNKNOWN":
        return {
            "action": "CLARIFY",
            "message": (
                "Parfait 🙂 Que souhaitez-vous faire ?\n"
                "1️⃣ Ajouter le produit au panier\n"
                "2️⃣ Voir d'autres produits similaires"
            )
        }

    return {
        "action": intent,
        "payload": state.pending_choice["payload"]
    }
