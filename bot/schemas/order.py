from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from db.models.order import OrderMode

class OrderCreate(BaseModel):
    id: int
    driver: Optional[int] = None         # теперь Optional
    ordernumb: Optional[str] = None      # теперь Optional
    region: str
    from_: str = Field(..., alias="from") # "_" чтобы не конфликтовало с ключевым словом Python
    to: str
    datetime: datetime
    car_class: str
    price_0: Optional[float] = None      # теперь Optional
    price: float
    mode: OrderMode
    flight: Optional[str] = None
    comment: Optional[str] = None
    contact: Optional[str] = None
    supplier: Optional[str] = None       # теперь Optional

    class Config:
        extra = 'ignore'
        allow_population_by_field_name = True
