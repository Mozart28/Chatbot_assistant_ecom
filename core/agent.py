import json
from core.prompt import SYSTEM_PROMPT, SUGGESTION_PROMPT
from core.memory import ConversationMemory
from tools.search_products import search_products
from tools.search_product_image import search_product_image
from tools.contact import request_contact
from core.tools_schema import TOOLS
#from core.llm_client import llm_client
from core.llm_client import get_llm_client

from tools.cart import add_product_to_cart


class CommercialAgent:
    def __init__(self, state=None):
        self.client = None
        self.memory = ConversationMemory()
        self.state = state
        self.current_product = None
        self.last_products_list = []
        self.last_suggestions = []

    def resolve_pending_choice(self, choice: str):
        """Handle user's choice when a pending decision exists"""
        pending = self.state.pending_choice
        
        if not pending:
            return {"type": "text", "message": "Aucun choix en attente."}
        
        options = pending.get("options", {})
        if choice not in options:
            return {"type": "text", "message": "Merci de répondre par 1 ou 2."}

        action = options[choice]
        self.state.pending_choice = None

        if action == "ADD_TO_CART":
            if self.current_product:
                return {"type": "add_to_cart", "product": self.current_product}
            else:
                return {"type": "text", "message": "❌ Produit introuvable."}

        if action == "SEE_MORE":
            return {"type": "text", "message": "Voici d'autres produits similaires 👇"}

        return {"type": "text", "message": "Action non reconnue."}

    def detect_ambiguous_response(self, user_input: str):
        """Detect if user response is ambiguous given the context"""
        lower_input = user_input.lower().strip()
        ambiguous_words = ['oui', 'ok', 'ouais', 'yes', 'd\'accord', 'bien sûr', 'parfait']
        
        if lower_input in ambiguous_words:
            if len(self.last_suggestions) > 1:
                return True
        return False

    def create_clarification_message(self):
        """Create a numbered clarification based on last suggestions"""
        if not self.last_suggestions:
            return None
        
        clarification = "Pour être sûr de bien comprendre, vous voulez :\n\n"
        for idx, suggestion in enumerate(self.last_suggestions, 1):
            clarification += f"{idx}️⃣ {suggestion}\n"
        clarification += "\nMerci de répondre avec le numéro (1, 2, etc.)"
        return clarification

    def extract_suggestions_from_text(self, text: str):
        """Extract multiple suggestions - IMPROVED FOR LLAMA COMPATIBILITY"""
        import re
        suggestions = []
        
        # PRIORITY 1: Numbered options - MORE PRECISE EXTRACTION
        numbered_pattern = r'[1-3]️⃣\s*([^\n]+?)(?=\s*[1-3]️⃣|\s*\n\s*Merci|$)'
        numbered_matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        if numbered_matches:
            clean_suggestions = []
            for match in numbered_matches:
                cleaned = match.strip()
                
                # Remove price patterns at start
                cleaned = re.sub(r'^Prix\s*:\s*\d+\s*\w+\s+', '', cleaned)
                cleaned = re.sub(r'^\d+\s*\w+\s+', '', cleaned)
                
                # Extract key action phrases
                if 'couleur' in cleaned.lower():
                    clean_suggestions.append('Quelle couleur')
                elif 'image' in cleaned.lower() or 'photo' in cleaned.lower():
                    clean_suggestions.append('Voir l\'image')
                elif 'acheter' in cleaned.lower() or 'panier' in cleaned.lower():
                    clean_suggestions.append('Ajouter au panier')
                elif 'autre' in cleaned.lower():
                    clean_suggestions.append('Autre produit')
                elif 'agent' in cleaned.lower() or 'contact' in cleaned.lower():
                    clean_suggestions.append('Contacter un agent')
                elif len(cleaned) > 5 and len(cleaned) < 50:
                    clean_suggestions.append(cleaned[:50])
            
            if clean_suggestions:
                return clean_suggestions[:3]
        
        # PRIORITY 2: "OU" pattern
        if " ou " in text.lower():
            sentences = re.split(r'[.!?]\s+', text)
            for sentence in sentences:
                if " ou " in sentence.lower():
                    parts = re.split(r'\s+ou\s+', sentence, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        for part in parts[:3]:
                            clean = re.sub(r'^(puis-je vous proposer|souhaitez-vous|voulez-vous|désirez-vous)\s+', '', part.strip(), flags=re.IGNORECASE)
                            clean = clean.strip('?,. ')
                            
                            if 'produit similaire' in clean.lower():
                                suggestions.append('Produit similaire')
                            elif 'agent' in clean.lower() or 'contact' in clean.lower():
                                suggestions.append('Contacter un agent')
                            elif 'image' in clean.lower():
                                suggestions.append('Voir l\'image')
                            elif 'panier' in clean.lower():
                                suggestions.append('Ajouter au panier')
                            elif len(clean) > 5:
                                suggestions.append(clean[:50])
                        if suggestions:
                            break
        
        # PRIORITY 3: Multiple questions
        if not suggestions:
            question_marks = text.count('?')
            if question_marks >= 2:
                questions = text.split('?')
                for q in questions:
                    q = q.strip()
                    if q and len(q) > 10:
                        if any(word in q.lower() for word in ['souhaitez', 'voulez', 'désirez', 'quel', 'quelle']):
                            if 'image' in q.lower():
                                suggestions.append('Voir l\'image')
                            elif 'panier' in q.lower():
                                suggestions.append('Ajouter au panier')
                            elif 'autre' in q.lower():
                                suggestions.append('Autre produit')
        
        # PRIORITY 4: Common patterns
        if not suggestions:
            common_patterns = [
                (r'voir (?:une |l\')image', 'Voir l\'image'),
                (r'voir (?:des |d\')autres?', 'Autres produits'),
                (r'ajouter (?:au )?panier', 'Ajouter au panier'),
                (r'contacter (?:un )?agent', 'Contacter un agent'),
            ]
            found_patterns = []
            for pattern, label in common_patterns:
                if re.search(pattern, text.lower()):
                    found_patterns.append(label)
            if len(found_patterns) >= 2:
                suggestions = found_patterns
        
        # Remove duplicates
        unique_suggestions = []
        seen = set()
        for s in suggestions:
            s_clean = s.lower().strip()
            if s_clean not in seen:
                seen.add(s_clean)
                unique_suggestions.append(s.strip())
        
        return unique_suggestions[:3]

    def handle_numbered_response(self, user_input: str):
        """Handle when user responds with a number"""
        lower_input = user_input.strip()
        
        if lower_input in ['1', '2', '3', '1️⃣', '2️⃣', '3️⃣']:
            number = int(lower_input[0])
            
            if number <= len(self.last_suggestions):
                chosen_suggestion = self.last_suggestions[number - 1]
                suggestion_lower = chosen_suggestion.lower()
                
                if "image" in suggestion_lower or "photo" in suggestion_lower:
                    return "montre moi l'image"
                elif "panier" in suggestion_lower:
                    return "ajouter au panier"
                elif "similaire" in suggestion_lower or "autre" in suggestion_lower:
                    return "montre moi d'autres produits similaires"
                elif "agent" in suggestion_lower or "contact" in suggestion_lower:
                    return "je veux contacter un agent"
                elif "couleur" in suggestion_lower:
                    return "quelle couleur est disponible"
                elif "continuer" in suggestion_lower:
                    return "oui continuer"
                elif "annul" in suggestion_lower or "abandonn" in suggestion_lower:
                    return "non annuler"
                else:
                    return chosen_suggestion
        
        return user_input

    def run(self, user_input: str):
        # Check if this is a clarification response
        if self.last_suggestions and user_input.strip() in ['1', '2', '3', '1️⃣', '2️⃣', '3️⃣']:
            user_input = self.handle_numbered_response(user_input)
            self.last_suggestions = []
        
        # Detect ambiguity
        if self.detect_ambiguous_response(user_input):
            clarification = self.create_clarification_message()
            if clarification:
                self.memory.add("user", user_input)
                self.memory.add("assistant", clarification)
                return {"type": "text", "message": clarification}
        
        # Add user message to memory
        self.memory.add("user", user_input)

        # Build messages for LLM
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += self.memory.get()
        messages.append({"role": "user", "content": user_input})

        # Pending choice handling
        if self.state.pending_choice:
            messages.insert(1, {
                "role": "system",
                "content": "Un choix est en attente. L'utilisateur doit répondre par un numéro (1 ou 2). Tu DOIS appeler le tool `handle_pending`."
            })

        # First LLM call
        llm = get_llm_client()
        response = llm.chat_complete(
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3
        )

        choice = response.choices[0]
        message = choice.message

        # No tool case
        if not message.tool_calls:
            answer = message.content or "Désolé, je n'ai pas pu traiter votre demande."
            self.memory.add("assistant", answer)
            self.last_suggestions = self.extract_suggestions_from_text(answer)
            return {"type": "text", "message": answer}

        # Handle tool_calls
        messages.append({"role": "assistant", "tool_calls": message.tool_calls})
        cart_action = None

        for call in message.tool_calls:
            tool_name = call.function.name
            raw_args = call.function.arguments or "{}"

            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            result = None

            if tool_name == "search_products":
                result = search_products(args.get("query", ""))
                self.current_product = None
                if isinstance(result, list):
                    self.last_products_list = result
                elif isinstance(result, dict) and 'products' in result:
                    self.last_products_list = result['products']

            elif tool_name == "search_product_image":
                result = search_product_image(args.get("query", ""))
                if isinstance(result, dict) and result.get("id"):
                    self.current_product = result
                    self.last_products_list = []

            elif tool_name == "request_contact":
                result = request_contact()

            elif tool_name == "add_product_to_cart":
                if self.current_product:
                    cart_action = {
                        "type": "add_to_cart",
                        "product": self.current_product.copy()
                    }
                    result = {
                        "success": True,
                        "message": f"Produit {self.current_product.get('name', '')} prêt à être ajouté au panier"
                    }
                    self.current_product = None
                else:
                    result = {"error": "Aucun produit sélectionné. Veuillez d'abord choisir un produit spécifique."}

            elif tool_name == "handle_pending":
                choice = args.get("choice", "").strip()
                return self.resolve_pending_choice(choice)

            else:
                result = {"error": f"Tool inconnu: {tool_name}"}

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })

        # If cart action triggered
        if cart_action:
            return cart_action

        # Second LLM call
        final_response = llm.chat_complete(
            messages=messages,
            temperature=0.4
        )

        final_answer = final_response.choices[0].message.content
        self.memory.add("assistant", final_answer)
        self.last_suggestions = self.extract_suggestions_from_text(final_answer)

        # Detect if we need to set pending choice
        if final_answer:
            text = final_answer.lower()
            if self.current_product and (("ajouter" in text and "ou" in text) or ("1" in text and "2" in text)):
                self.state.set_pending_choice(
                    choice_type="POST_PRODUCT_DECISION",
                    payload={"options": {"1": "ADD_TO_CART", "2": "SEE_MORE"}}
                )

        return {
            "type": "text",
            "message": final_answer,
            "pending_choice": self.state.pending_choice
        }
