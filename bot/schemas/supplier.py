from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from db.models.order import OrderMode

class SupplierCreate(BaseModel):
    name: str
