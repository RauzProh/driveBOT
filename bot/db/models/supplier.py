# supplier.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class Supplier(Base):
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)

    # связь "один поставщик — много заказов"
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="supplier")
