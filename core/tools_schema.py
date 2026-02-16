TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Recherche des produits disponibles dans le catalogue",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_product_image",
            "description": "Retourne l’image d’un produit si disponible",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_contact",
            "description": "Doit appeler cette fonction quand l'utilisateur demande le contact d'un agent.Donne les informations de contact du service commercial avec un rating sous forme d'#etoiles",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "add_product_to_cart",
            "description": "Ajoute un produit au panier quand le client confirme l'achat",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
          "type": "function",
          "function": {
          "name": "handle_pending_choice",
           "description": "Résout un choix en attente (oui/non, option 1/2, etc.)",
           "parameters": {
            "type": "object",
           "properties": {
            "choice": {
            "type": "string",
            "description": "Choix exprimé par l'utilisateur (oui, non, 1, 2, etc.)"
        }
      },
      "required": ["choice"]
    }
  }
}

]
