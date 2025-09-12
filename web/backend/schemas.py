from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OrderRequest(BaseModel):
    region: str
    from_: str = Field(..., alias="from") 
    to: str
    datetime: datetime
    car_class: str
    price: float
    mode: str
    flight: Optional[str] = None
    comment: Optional[str] = None
    contact: Optional[str] = None
