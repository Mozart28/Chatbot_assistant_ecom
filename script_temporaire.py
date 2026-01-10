
from pinecone import Pinecone
from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)

if PINECONE_INDEX_NAME in pc.list_indexes().names():
    pc.delete_index(PINECONE_INDEX_NAME)
    print("Index supprimé")
