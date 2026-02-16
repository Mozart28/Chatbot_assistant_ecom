
# core/intents.py

ADD_TO_CART = ["ajouter", "prendre", "acheter", "1"]
SEE_MORE = ["voir", "autres", "similaires", "2"]

def detect_intent(user_input: str):
    text = user_input.lower()
    if any(k in text for k in ADD_TO_CART):
        return "ADD_TO_CART"
    if any(k in text for k in SEE_MORE):
        return "SEE_MORE"
    return "UNKNOWN"
