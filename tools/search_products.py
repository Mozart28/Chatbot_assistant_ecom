# search_products.py - FIXED to handle PDFs
from retrieval.retriever import ProductRetriever
from catalog.validator import products_to_context
from rapidfuzz import fuzz
import streamlit as st

retriever = ProductRetriever()

@st.cache_data
def search_products(query: str) -> str:
    """
    Recherche des produits ET documents PDF correspondant à la requête.
    - Gère à la fois les produits (JSON) et les PDFs uploadés
    - Utilise une recherche floue pour gérer pluriel/singulier et petites fautes
    """
    results = retriever.search(query)
    
    if not results:
        return "Aucun produit trouvé."
    
    query_lower = query.lower()
    
    # Séparer les produits et les PDFs
    products = []
    pdf_matches = []
    
    for item in results:
        # Check if it's a Product object or a dict (PDF document)
        if hasattr(item, 'name'):  # It's a Product object
            # Filtrage avec recherche floue
            if (fuzz.partial_ratio(query_lower, item.name.lower()) > 70 or 
                fuzz.partial_ratio(query_lower, item.category.lower()) > 70):
                products.append(item)
        
        elif isinstance(item, dict):  # It's a PDF document
            # Check if query matches text content
            text = item.get('text', '')
            if query_lower in text.lower() or fuzz.partial_ratio(query_lower, text.lower()) > 75:
                pdf_matches.append(item)
    
    # Build response
    response_parts = []
    
    # Add products
    if products:
        response_parts.append(products_to_context(products))
    
    # Add PDF matches
    if pdf_matches:
        pdf_text = "\n\n📄 **Produits supplémentaires trouvés:**\n\n"
        for pdf in pdf_matches:
            # Extract product info from PDF text
            text = pdf.get('text', '')
            
            # Try to extract key info
            lines = text.split('\n')
            product_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'name' in key:
                        product_info['name'] = value
                    elif 'price' in key:
                        product_info['price'] = value
                    elif 'category' in key:
                        product_info['category'] = value
                    elif 'description' in key:
                        product_info['description'] = value
                    elif 'stock' in key and 'quantity' in key:
                        product_info['stock'] = value
            
            # Format the info
            if product_info:
                pdf_text += f"**{product_info.get('name', 'Produit')}**\n"
                if 'category' in product_info:
                    pdf_text += f"  - Catégorie: {product_info['category']}\n"
                if 'description' in product_info:
                    pdf_text += f"  - Description: {product_info['description']}\n"
                if 'price' in product_info:
                    pdf_text += f"  - Prix: {product_info['price']}\n"
                if 'stock' in product_info:
                    pdf_text += f"  - Stock: {product_info['stock']}\n"
                pdf_text += "\n"
        
        response_parts.append(pdf_text)
    
    if not response_parts:
        return f"Aucun produit trouvé pour '{query}'."
    
    return "\n".join(response_parts)
