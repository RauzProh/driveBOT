# order.py
from sqlalchemy import Integer, String, ForeignKey, Enum, DECIMAL, TIMESTAMP, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
import enum
from datetime import datetime
from typing import Optional
from .supplier import Supplier  # импорт модели поставщика

class OrderStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

class OrderMode(enum.Enum):
    FCFS = "fcfs"
    AUCTION = "auction"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ordernumb: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_address: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    car_class: Mapped[str] = mapped_column(String(50), nullable=False)
    price_0: Mapped[float] = mapped_column(DECIMAL(10,2), default=None)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), default=None)
    mode: Mapped[OrderMode] = mapped_column(Enum(OrderMode), default=OrderMode.FCFS)
    trip_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    passenger_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.NEW)

    driver_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("users.id"), nullable=True)
    driver: Mapped["User"] = relationship("User", back_populates="orders")

    # связь с поставщиком
    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.id"), nullable=True)
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="orders")

    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="order", cascade="all, delete-orphan")
    messages = relationship("OrderMessage", back_populates="order", cascade="all, delete-orphan")
