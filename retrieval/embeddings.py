
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL_NAME


def get_embeddings():
    """
    Singleton embeddings model
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )
