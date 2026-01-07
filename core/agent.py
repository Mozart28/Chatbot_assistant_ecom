from mistralai import Mistral
from core.prompt import SYSTEM_PROMPT,SUGGESTION_PROMPT
from core.router import route_intent
from core.memory import ConversationMemory
from tools.search_products import search_products
from config.settings import MISTRAL_API_KEY




class CommercialAgent:
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.memory = ConversationMemory()

    def run(self, user_input: str) -> str:
        # 1️⃣ Mémoire
        self.memory.add("user", user_input)

        # 2️⃣ Détection d’intention
        intent = route_intent(user_input)

        # 3️⃣ Messages de base
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += self.memory.get()

        # 4️⃣ Si besoin d’un tool → enrichir le contexte
        if intent == "product_search":
            context = search_products(user_input)

            if context:
                messages.append({
                    "role": "system",
                    "content": f"CONTEXTE PRODUITS DISPONIBLES :\n{context}"
                })

        # 5️⃣ Ajouter prompt de suggestion
        messages.append({"role": "system", "content": SUGGESTION_PROMPT})

        # 6️⃣ Ajouter la question utilisateur
        messages.append({"role": "user", "content": user_input})

        # 7️⃣ Appel LLM
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=messages
        )

        answer = response.choices[0].message.content

        # 8️⃣ Mémoire
        self.memory.add("assistant", answer)

        return answer
