from sqlalchemy import Integer, String, ForeignKey, Enum, DECIMAL, TIMESTAMP, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
import enum
from datetime import datetime

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
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    to_address: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    car_class: Mapped[str] = mapped_column(String(50), nullable=False)  # эко/комфорт/бизнес
    price: Mapped[float] = mapped_column(DECIMAL(10,2), default=None)
    mode: Mapped[OrderMode] = mapped_column(Enum(OrderMode), default=OrderMode.FCFS)
    comments: Mapped[str] = mapped_column(String(255), default=None)
    passenger_info: Mapped[str] = mapped_column(String(255), default=None)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.NEW)

    driver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    driver: Mapped["User"] = relationship("User", back_populates="orders")

    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="order", cascade="all, delete-orphan")
