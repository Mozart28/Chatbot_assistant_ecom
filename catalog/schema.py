
from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    id: str
    name: str
    category: str
    description: str
    price: float
    currency: str
    in_stock: bool
    stock_quantity: Optional[int] = None
    
