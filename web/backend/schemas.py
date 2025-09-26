from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OrderRequest(BaseModel):
    driver: int
    id: int
    ordernumb: str
    region: str
    from_: str = Field(..., alias="from") 
    to: str
    datetime: datetime
    car_class: str
    price_0: float
    price: float
    mode: str
    flight: Optional[str] = None
    comment: Optional[str] = None
    contact: Optional[str] = None
    supplier: str

    class Config:
        extra = 'ignore'

class SupplierRequest(BaseModel):
    name: str
