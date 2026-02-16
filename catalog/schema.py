from dataclasses import dataclass, field
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
    image_url: Optional[str] = None
    type: str = field(default="product", init=False)  # ✅ champ fixe, non modifiable à l'init
