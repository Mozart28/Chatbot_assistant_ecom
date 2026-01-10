
from typing import List, Dict

class ConversationMemory:
    """
    Mémoire conversationnelle bufferisée pour un assistant.
    Permet de stocker les échanges et de limiter le nombre de messages
    pour optimiser les performances.
    """

    def __init__(self, buffer_limit: int = 10):
        self.buffer_limit = buffer_limit
        self.memory: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        """
        Ajoute un message dans la mémoire.
        role: "user" ou "assistant"
        content: texte du message
        """
        self.memory.append({"role": role, "content": content})
        # Limiter la mémoire pour ne conserver que les derniers buffer_limit messages
        if len(self.memory) > self.buffer_limit:
            self.memory = self.memory[-self.buffer_limit:]

    def get(self) -> List[Dict[str, str]]:
        """
        Retourne la liste des messages mémorisés pour le LLM.
        Limité aux derniers messages pour les performances.
        """
        return self.memory.copy()

    def get_last_assistant(self) -> str:
        """
        Retourne le dernier message de l'assistant pour fournir un contexte.
        Si aucun message assistant n'existe, retourne une chaîne vide.
        """
        for msg in reversed(self.memory):
            if msg["role"] == "assistant":
                return msg["content"]
        return ""
