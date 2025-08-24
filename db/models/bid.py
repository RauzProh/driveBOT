from sqlalchemy import Integer, ForeignKey, DECIMAL, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from datetime import datetime
from typing import Optional

class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    eta_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    order: Mapped["Order"] = relationship("Order", back_populates="bids")
    driver: Mapped["User"] = relationship("User")
