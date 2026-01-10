
from config.settings import MISTRAL_API_KEY
import asyncio
from mistralai import Mistral

client = Mistral(api_key=MISTRAL_API_KEY)

async def chat_handler(messages):
    response = await client.chat.complete_async(
        model="mistral-small-latest",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content


