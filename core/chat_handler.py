
from mistralai import Mistral
from config.settings import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

def chat_handler(user_input: str, memory: list) -> str:
    messages = memory + [
        {"role": "user", "content": user_input}
    ]

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
