from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from db.models.order import OrderMode

class OrderCreate(BaseModel):
    region: str
    from_: str  # "_" чтобы не конфликтовало с ключевым словом Python
    to: str
    datetime: datetime
    car_class: str
    price: float
    mode: OrderMode
    flight: Optional[str] = None
    comment: Optional[str] = None
    contact: Optional[str] = None
