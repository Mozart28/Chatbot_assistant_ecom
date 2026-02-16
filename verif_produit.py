from retrieval.retriever import ProductRetriever

retriever = ProductRetriever(top_k=5)
query = "Polo homme casual"
products = retriever.search(query)
print(products)  # affiche objets Product
