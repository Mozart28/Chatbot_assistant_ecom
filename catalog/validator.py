
from typing import List
from catalog.schema import Product


def filter_available_products(products: List[Product]) -> List[Product]:
    return [
        p for p in products
        if p.in_stock and (p.stock_quantity is None or p.stock_quantity > 0)
    ]


def products_to_context(products: List[Product]) -> str:
    if not products:
        return "Aucun produit disponible."

    lines = []
    for p in products:
        lines.append(
            f"{p.name}\n"
            f"  Prix: {p.price} {p.currency}\n"
            
        )
    return "\n".join(lines)

