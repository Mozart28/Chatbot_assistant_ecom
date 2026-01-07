
from retrieval.retriever import ProductRetriever
from catalog.validator import products_to_context

retriever = ProductRetriever()

def search_products(query: str) -> str:
    products = retriever.search(query)

    if not products:
        return ""

    return products_to_context(products)
