
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# --- Pinecone ---
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "shop-catalog")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

# --- Embeddings ---
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
EMBEDDING_DIMENSION = 1024

# --- RAG ---
TOP_K_RESULTS = 5

# -- ADMIN KEY -- #

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")

# --- App ---
APP_NAME = "Assistant Commercial IA"
