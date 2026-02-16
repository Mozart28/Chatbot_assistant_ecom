"""
Dynamic LLM Client - Mistral + Groq + Hugging Face
Automatically switches between providers
"""

import json
import os
from mistralai import Mistral

class DynamicLLMClient:
    """Multi-provider LLM client"""
    
    def __init__(self):
        self.load_config()
        self.initialize_client()
    
    def load_config(self):
        """Load current model configuration"""
        config_file = 'config/llm_config.json'
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.provider = config.get('provider', 'mistral')
                self.model = config.get('model', 'mistral-small-latest')
        else:
            self.provider = 'mistral'
            self.model = 'mistral-small-latest'
        
        print(f"🤖 Using {self.provider}/{self.model}")
    
    def initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == 'mistral':
            from config.settings import MISTRAL_API_KEY
            self.client = Mistral(api_key=MISTRAL_API_KEY)
            self.chat_method = self._mistral_chat
        
        elif self.provider == 'groq':
            try:
                from groq import Groq
                groq_api_key = os.getenv('GROQ_API_KEY')
                if not groq_api_key:
                    raise ValueError("GROQ_API_KEY not found in environment")
                self.client = Groq(api_key=groq_api_key)
                self.chat_method = self._groq_chat
                print("✅ Groq client initialized")
            except ImportError:
                raise ImportError("groq package not installed. Run: pip install groq")
        
        elif self.provider == 'huggingface':
            try:
                from huggingface_hub import InferenceClient
                hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
                if not hf_api_key:
                    raise ValueError("HUGGINGFACE_API_KEY not found in environment")
                self.client = InferenceClient(token=hf_api_key)
                self.chat_method = self._huggingface_chat
                print("✅ Hugging Face client initialized")
            except ImportError:
                raise ImportError("huggingface_hub not installed. Run: pip install huggingface_hub")
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def chat_complete(self, messages, tools=None, tool_choice="auto", temperature=0.3):
        """Unified chat completion interface"""
        return self.chat_method(messages, tools, tool_choice, temperature)
    
    def _mistral_chat(self, messages, tools, tool_choice, temperature):
        """Mistral AI chat completion"""
        response = self.client.chat.complete(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature
        )
        self._log_usage(response)
        return response
    
    def _groq_chat(self, messages, tools, tool_choice, temperature):
        """Groq chat completion"""
        # Groq uses OpenAI-compatible API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools if tools else None,
            temperature=temperature,
            max_tokens=4096
        )
        
        # Convert to Mistral-like response format for compatibility
        class GroqResponse:
            def __init__(self, groq_resp):
                self.choices = []
                for choice in groq_resp.choices:
                    class Choice:
                        def __init__(self, groq_choice):
                            self.message = groq_choice.message
                    self.choices.append(Choice(choice))
                self.usage = groq_resp.usage
        
        adapted_response = GroqResponse(response)
        self._log_usage(adapted_response)
        return adapted_response
    
    def _huggingface_chat(self, messages, tools, tool_choice, temperature):
        """Hugging Face Inference API chat completion"""
        # HF uses different format - convert messages
        conversation = []
        for msg in messages:
            if msg['role'] == 'system':
                # Add system message as first user message
                conversation.insert(0, {
                    'role': 'user',
                    'content': f"System: {msg['content']}"
                })
            elif msg['role'] in ['user', 'assistant']:
                conversation.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # HF Inference API call
        response_text = self.client.chat_completion(
            messages=conversation,
            model=self.model,
            max_tokens=2048,
            temperature=temperature
        )
        
        # Convert to Mistral-like format
        class HFResponse:
            def __init__(self, text):
                self.choices = []
                class Choice:
                    def __init__(self, content):
                        class Message:
                            def __init__(self, text):
                                self.content = text
                                self.tool_calls = None
                        self.message = Message(content)
                self.choices.append(Choice(text))
                self.usage = None  # HF doesn't return token usage easily
        
        # Extract text from response
        if hasattr(response_text, 'choices'):
            text = response_text.choices[0].message.content
        else:
            text = str(response_text)
        
        adapted_response = HFResponse(text)
        self._log_usage(adapted_response, estimated_tokens=len(text.split()) * 1.3)
        return adapted_response
    
    def _log_usage(self, response, estimated_tokens=None):
        """Log token usage to super admin"""
        try:
            # Extract token count
            if estimated_tokens:
                tokens = int(estimated_tokens)
            elif self.provider == 'mistral':
                usage = getattr(response, 'usage', None)
                tokens = usage.total_tokens if usage else 0
            elif self.provider == 'groq':
                usage = getattr(response, 'usage', None)
                tokens = usage.total_tokens if usage else 0
            elif self.provider == 'huggingface':
                # HF doesn't provide token count easily
                tokens = 0
            else:
                tokens = 0
            
            # Calculate cost
            cost = self._calculate_cost(tokens)
            
            # Send to super admin backend
            import requests
            requests.post('http://localhost:5004/superadmin/usage/log', json={
                'model': self.model,
                'tokens': tokens,
                'cost': cost
            }, timeout=1)
        
        except Exception as e:
            print(f"⚠️ Failed to log usage: {e}")
    
    def _calculate_cost(self, tokens):
        """Calculate cost based on model"""
        costs = {
            # Mistral
            'mistral-tiny': 0.14,
            'open-mistral-7b': 0.25,
            'mistral-small-latest': 2.0,
            'mistral-large-latest': 8.0,
            # Groq (ultra-fast!)
            'llama-3.1-70b-versatile': 0.59,
            'llama-3.1-8b-instant': 0.05,
            'llama-3.3-70b-versatile': 0.59,
            'mixtral-8x7b-32768': 0.24,
            # Hugging Face (gratuit!)
            'meta-llama/Llama-3.2-3B-Instruct': 0.00,
            'meta-llama/Llama-3.1-8B-Instruct': 0.00,
        }
        
        cost_per_1m = costs.get(self.model, 0.25)
        return (tokens / 1_000_000) * cost_per_1m
    
    def reload_config(self):
        """Reload configuration for hot-swapping"""
        self.load_config()
        self.initialize_client()


# Global instance
llm_client = DynamicLLMClient()
