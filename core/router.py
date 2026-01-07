
from mistralai import Mistral
from config.settings import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

INTENT_PROMPT = """
Tu es un classificateur d'intentions pour un assistant e-commerce.

Catégories possibles :
- product_search
- chat
- unknown

Réponds uniquement par le nom de la catégorie.
"""

def route_intent_llm(user_input: str) -> str:
    messages = [
        {"role": "system", "content": INTENT_PROMPT},
        {"role": "user", "content": user_input}
    ]

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        temperature=0
    )

    intent = response.choices[0].message.content.strip().lower()

    if intent not in ["product_search", "chat"]:
        return "chat"

    return intent




def route_intent(user_input: str) -> str:
    text = user_input.lower()

    fast_keywords = [
        "prix", "acheter", "commande", "disponible",
        "baskets", "chaussures", "t-shirt", "casquette"
    ]

    if any(k in text for k in fast_keywords):
        return "product_search"

    return route_intent_llm(user_input)

