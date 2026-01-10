from mistralai import Mistral
from core.prompt import SYSTEM_PROMPT, SUGGESTION_PROMPT
from core.router import route_intent
from core.memory import ConversationMemory
from tools.search_products import search_products
from config.settings import MISTRAL_API_KEY
from config.contact import CONTACT_INFO
from tools.search_product_image import search_product_image



class CommercialAgent:
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.memory = ConversationMemory()

    def run(self, user_input: str) -> str:
        # 1️⃣ Mémoire utilisateur
        self.memory.add("user", user_input)

        # 2️⃣ Détection d’intention
        intent = route_intent(user_input)

        # 3️⃣ Messages de base
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Limiter la mémoire pour la performance
        messages += self.memory.get()

                # 2️⃣ Détection d’intention
        intent = route_intent(user_input)

        # 🎯 CAS CONTACT HUMAIN → SORTIE IMMÉDIATE
        if intent == "request_contact":
            message = (
                "Parfait 😊\n\n"
                "Voici comment contacter notre service commercial :\n\n"
                f"📧 Email : {CONTACT_INFO['email']}\n"
                f"📞 Téléphone : {CONTACT_INFO['phone']}\n"
                f"💬 WhatsApp : {CONTACT_INFO['whatsapp']}"
            )

            # Sauvegarde mémoire assistant
            self.memory.add("assistant", message)

            return message

        # 4️⃣ Enrichissement RAG si besoin
        if intent == "product_search":
            context = search_products(user_input)
            if context:
                messages.append({
                    "role": "system",
                    "content": f"CONTEXTE PRODUITS DISPONIBLES :\n{context}"
                })

        if intent == "product_image":
            product = search_product_image(user_input)
            if product:
                self.memory.add("assistant", f"IMAGE::{product['name']}")
                return {
            "type": "product_image",
            "product": product
        }
            else:
                message = (
            "Désolé 😕 je n’ai pas trouvé ce produit dans notre stock.\n\n"
            "👉 Vous pouvez :\n"
            "- vérifier le nom du produit\n"
            "- voir des produits similaires\n"
            "- contacter un conseiller"
        )

        

    
        


        self.memory.add("assistant", message)
        return {
            "type": "text",
            "message": message
        }


        # 5️⃣ Prompt de suggestion
        messages.append({"role": "system", "content": SUGGESTION_PROMPT})

        # 6️⃣ Ajouter le dernier contexte assistant si disponible
        last_context = self.memory.get_last_assistant()
        if last_context:
            messages.append({
                "role": "system",
                "content": f"Dernier contexte / suggestion précédente :\n{last_context}"
            })

        # 7️⃣ Question utilisateur
        messages.append({"role": "user", "content": user_input})

        # 8️⃣ Appel LLM
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.4
        )

        answer = response.choices[0].message.content

        # 9️⃣ Mémoire assistant
        self.memory.add("assistant", answer)

        return answer
