
from typing import List
from catalog.schema import Product


def filter_available_products(products: List[Product]) -> List[Product]:
    return [
        p for p in products
        if p.in_stock and (p.stock_quantity is None or p.stock_quantity > 0)
    ]


def products_to_context(products: List[Product]) -> str:
    """
    Convertit les produits en texte STRICT pour le LLM
    """
    lines = []
    for p in products:
        lines.append(
            f"- {p.name} | {p.category} | {p.price} {p.currency}\n"
            f"  Description: {p.description}"
        )
    return "\n".join(lines)
