# core/state_manager.py

class ConversationState:
    def __init__(self):
        self.pending_choice = None

    def set_pending_choice(self, choice_type, payload=None):
        self.pending_choice = {
            "type": choice_type,
            "payload": payload
        }

    def clear(self):
        self.pending_choice = None
