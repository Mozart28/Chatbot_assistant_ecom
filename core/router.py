
from mistralai import Mistral
from config.settings import MISTRAL_API_KEY
from core.prompt import SYSTEM_PROMPT

client = Mistral(api_key=MISTRAL_API_KEY)

INTENTS = [
    "product_search",
    "product_image",
    "request_contact",
    "chat"
]

CONTACT_SIGNAL = "CONTACT_REQUEST_CONFIRMED"


def route_intent_llm(user_input: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
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

    contact_keywords = [
        "d'accord", 
        "contact", "conseiller", "agent",
        "téléphone", "whatsapp", "email","humain","un commercial","numéro"
    ]

    if any(k in text for k in contact_keywords):
        return "request_contact"

    fast_keywords = [
        "prix", "acheter", "commande", "disponible",
        "baskets", "chaussures", "t-shirt", "casquette","t shirt","baskets",
        "chemises","polo","oui"
    ]
    

    if any(k in text for k in fast_keywords):
        return "product_search"

    image_keywords = [
    "photo", "image", "voir", "montre", "à quoi ressemble",
    "apparence", "picture"
]

    if any(k in text for k in image_keywords):
        return "product_image"




    return route_intent_llm(user_input)

