from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OrderRequest(BaseModel):
    driver: Optional[int] = None       # теперь Optional
    id: Optional[int] = None
    ordernumb: Optional[str] = None    # тоже Optional
    region: str
    from_: str = Field(..., alias="from")
    to: str
    datetime: datetime
    car_class: str
    price_0: Optional[float] = None
    price: float
    mode: str
    flight: Optional[str] = None
    comment: Optional[str] = None
    contact: Optional[str] = None
    supplier: Optional[str] = None     # теперь Optional

    class Config:
        extra = 'ignore'
        allow_population_by_field_name = True


class SupplierRequest(BaseModel):
    name: str
