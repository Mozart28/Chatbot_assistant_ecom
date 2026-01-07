import json
from pathlib import Path
from typing import List
from catalog.schema import Product

# Chemin relatif au fichier loader.py
CATALOG_PATH = Path(__file__).parent.parent / "products" / "catalog.json"

def load_catalog() -> List[Product]:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"catalog.json introuvable à {CATALOG_PATH}")

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = []
    for item in data:
        products.append(Product(**item))

    return products

    print("Chemin JSON :", CATALOG_PATH)
    print("Existe ?", CATALOG_PATH.exists())

