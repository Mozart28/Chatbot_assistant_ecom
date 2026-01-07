from mistralai import Mistral
from core.prompt import SYSTEM_PROMPT
from core.router import route_intent
from core.memory import ConversationMemory
from tools.search_products import search_products
from config.settings import MISTRAL_API_KEY



class CommercialAgent:
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.memory = ConversationMemory()

    def run(self, user_input: str) -> str:
        self.memory.add("user", user_input)
        intent = route_intent(user_input)

        if intent == "product_search":
            products = search_products(user_input)

            if not products:
                answer = "Désolé, aucun produit correspondant n’est disponible actuellement."
                self.memory.add("assistant", answer)
                return answer

            # ✅ Accès par attributs Product
            context_text = products

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"QUESTION : {user_input}\n\nCONTEXTE PRODUITS :\n{context_text}"
                }
            ]

        else:
            # Conversation libre
            context_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.memory.get()
            context_messages.append({"role": "user", "content": user_input})
            messages = context_messages

        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=messages
        )

        answer = response.choices[0].message.content
        self.memory.add("assistant", answer)
        return answer
