from retrieval.retriever import ProductRetriever


retriever = ProductRetriever()
products = retriever.search("T-shirt homme basique", intent="product_search")
print([p.name for p in products])
